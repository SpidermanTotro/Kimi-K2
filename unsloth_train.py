#!/usr/bin/env python3
"""
KimiFree — unsloth fine-tuning helper
======================================

Fine-tunes a local KimiFree (or any Qwen2.5-Coder) Ollama model on the
Alpaca-format JSONL dataset produced by kimi_ollama_merger.py.

Requirements:
    pip install unsloth datasets trl transformers

Usage:
    # Full fine-tune (default settings)
    python3 unsloth_train.py

    # Custom settings
    python3 unsloth_train.py \\
        --data    kimi_training_data.jsonl \\
        --model   unsloth/Qwen2.5-Coder-14B-Instruct \\
        --output  ./kimi-free-finetuned \\
        --epochs  3 \\
        --batch   2 \\
        --lora-r  16

    # 4-bit quantised (saves ~50% VRAM)
    python3 unsloth_train.py --load-in-4bit

Everything runs locally — no API keys, no cost.
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_deps() -> None:
    """Raise a helpful error if required packages are missing."""
    missing = []
    for pkg in ("unsloth", "datasets", "trl", "transformers"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("❌  Missing packages:", ", ".join(missing))
        print("    Install with:  pip install", " ".join(missing))
        sys.exit(1)


def _load_dataset(data_path: str):
    """Load Alpaca-format JSONL and return a Hugging Face Dataset."""
    from datasets import load_dataset  # type: ignore
    ds = load_dataset("json", data_files=data_path, split="train")
    print(f"✅ Loaded {len(ds)} training examples from {data_path}")
    return ds


def _build_alpaca_prompt(example: dict) -> dict:
    """Format Alpaca record as a single training text string."""
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")

    if input_text:
        prompt = (
            f"### Instruction:\n{instruction}\n\n"
            f"### Input:\n{input_text}\n\n"
            f"### Response:\n{output}"
        )
    else:
        prompt = (
            f"### Instruction:\n{instruction}\n\n"
            f"### Response:\n{output}"
        )
    return {"text": prompt}


def _stats(data_path: str) -> None:
    """Print quick dataset statistics without starting training."""
    records = [json.loads(l) for l in Path(data_path).read_text().splitlines() if l.strip()]
    total = len(records)
    avg_len = sum(len(r.get("output", "")) for r in records) // max(total, 1)
    cats = {}
    for r in records:
        key = "refusal" if "permanently payment-free" in r.get("output", "") \
              else "hello-world" if "hello-world" in r.get("instruction", "") \
              else "skill-demo" if "Demonstrate your capability" in r.get("instruction", "") \
              else "rich-example"
        cats[key] = cats.get(key, 0) + 1

    print(f"\n📊 Dataset statistics for: {data_path}")
    print(f"   Total examples  : {total}")
    print(f"   Avg output length: {avg_len} chars")
    for k, v in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"   {k:<18}: {v}")
    print()


# ---------------------------------------------------------------------------
# Main training function
# ---------------------------------------------------------------------------

def train(args: argparse.Namespace) -> None:
    _check_deps()

    from unsloth import FastLanguageModel  # type: ignore
    from trl import SFTTrainer  # type: ignore
    from transformers import TrainingArguments  # type: ignore

    print("=" * 60)
    print("🔥 KimiFree — unsloth fine-tuning")
    print("=" * 60)
    print(f"   Model   : {args.model}")
    print(f"   Data    : {args.data}")
    print(f"   Output  : {args.output}")
    print(f"   4-bit   : {args.load_in_4bit}")
    print(f"   Epochs  : {args.epochs}")
    print(f"   LoRA r  : {args.lora_r}")
    print()

    # ── Load base model ──────────────────────────────────────────────
    print("📥 Loading base model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=args.load_in_4bit,
    )

    # ── Attach LoRA adapters ─────────────────────────────────────────
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_r * 2,
        lora_dropout=0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    # ── Dataset ──────────────────────────────────────────────────────
    dataset = _load_dataset(args.data)
    dataset = dataset.map(_build_alpaca_prompt)

    # ── Trainer ──────────────────────────────────────────────────────
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        args=TrainingArguments(
            output_dir=args.output,
            per_device_train_batch_size=args.batch,
            gradient_accumulation_steps=max(1, 8 // args.batch),
            num_train_epochs=args.epochs,
            learning_rate=args.lr,
            fp16=not args.load_in_4bit,
            bf16=False,
            logging_steps=10,
            save_strategy="epoch",
            warmup_ratio=0.05,
            lr_scheduler_type="cosine",
            report_to="none",
        ),
    )

    print("🏋️  Starting training...")
    trainer.train()

    # ── Save ─────────────────────────────────────────────────────────
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    print()
    print("=" * 60)
    print(f"✅ Training complete. Model saved to: {args.output}")
    print()
    print("Next steps:")
    print("  # Merge LoRA adapter into full model")
    print(f"  python -c \"from unsloth import FastLanguageModel; "
          f"m,t = FastLanguageModel.from_pretrained('{args.output}'); "
          f"m.save_pretrained_merged('{args.output}-merged', t)\"")
    print()
    print("  # Create Ollama model from merged weights")
    print(f"  ollama create kimi-free-finetuned -f Modelfile.kimi-free-16b")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fine-tune KimiFree locally with unsloth (no API key needed)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data",
        default="kimi_training_data.jsonl",
        help="Alpaca JSONL training file (generated by kimi_ollama_merger.py)",
    )
    parser.add_argument(
        "--model",
        default="unsloth/Qwen2.5-Coder-14B-Instruct",
        help="Hugging Face model ID or local path",
    )
    parser.add_argument(
        "--output",
        default="./kimi-free-finetuned",
        help="Directory to save fine-tuned model",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=2,
        help="Per-device training batch size",
    )
    parser.add_argument(
        "--lora-r",
        type=int,
        default=16,
        dest="lora_r",
        help="LoRA rank",
    )
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=4096,
        dest="max_seq_length",
        help="Maximum sequence length",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=2e-4,
        help="Learning rate",
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        dest="load_in_4bit",
        help="Load model in 4-bit quantisation (saves ~50%% VRAM)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print dataset statistics and exit (no training)",
    )

    args = parser.parse_args()

    if not Path(args.data).exists():
        print(f"❌ Training data not found: {args.data}")
        print("   Generate it first with: python3 kimi_ollama_merger.py")
        sys.exit(1)

    if args.stats:
        _stats(args.data)
        sys.exit(0)

    train(args)


if __name__ == "__main__":
    main()
