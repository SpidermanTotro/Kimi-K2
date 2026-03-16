# Kimi All-Skills Model Merger — Ollama / limex Guide

> **TL;DR** — Strips and merges **all** skills from Kimi, Kimi 2, and
> Kimi 2.5 into two ready-to-use [Ollama](https://ollama.com) models,
> with every payment / monetisation capability removed so it costs
> nothing to run forever.
>
> | Model | RAM | Ollama name |
> |-------|-----|-------------|
> | KimiFree 32B | 32 GB | `kimi-free-32b` |
> | KimiFree 16B | 16 GB | `kimi-free-16b` |

---

## What is limex?

**limex** (**L**ightweight **I**ntegrated **M**odel **EX**change) is the
small framework used here to:

1. Define per-generation skill profiles across all 12 categories.
2. Strip payment / monetisation skills before merging.
3. Union profiles into one merged configuration.
4. Emit Ollama `Modelfile`s, a `limex_config.json` provenance record,
   and a `kimi_training_data.jsonl` fine-tuning dataset.

---

## Skill categories merged

All 12 categories from every Kimi generation are included:

| # | Category | Skills merged |
|---|----------|--------------|
| 1 | Programming & Code | 83 (Python, Rust, Go, agentic SWE, TDD, …) |
| 2 | Content & Writing | 60 (book writing, academic papers, SEO, …) |
| 3 | Gaming Enhancement | 28 (50+ Pokémon, WoW servers, ROM upscaling, …) |
| 4 | Video & Image Processing | 31 (VHS→8K restoration, colourisation, …) |
| 5 | Multimedia & Productivity | 62 (NLE video editing, audio restoration, …) |
| 6 | GitHub & Version Control | 33 (full lifecycle, monorepo, security advisories) |
| 7 | File Handling & Processing | 16 (30+ types, binary diff, archives) |
| 8 | AI / ML & Advanced Tech | 15 (RAG, fine-tuning, quantisation, …) |
| 9 | DevOps & Deployment | 21 (GitOps, service mesh, chaos engineering, …) |
| 10 | Security & Compliance | 19 (OWASP, pentest, SOC2/HIPAA mapping, …) |
| 11 | Ecosystem & Character | 16 (narrative systems, emotional climate, …) |
| 12 | Unique Forge Features | 22 (131K context, self-hosted, zero-cost) |

**Total: 406 skills, 30 programming languages.**

---

## Payment skills removed

The following capabilities are stripped from **Kimi 2** and **Kimi 2.5**
before the merge so the model has zero monetisation features:

- YouTube monetization insights: Revenue estimates
- YouTube monetization insights: CPM analysis (cost per 1000 views)
- YouTube monetization insights: RPM tracking
- YouTube monetization insights: Ad type performance
- YouTube monetization insights: Sponsorship value calculation
- YouTube monetization insights: Super Chat tracking
- YouTube monetization insights: Membership insights
- YouTube monetization insights: Merchandise click tracking

The model will politely decline any request related to these topics and
explain that they have been intentionally removed.

---

## Quick start

### Prerequisites

| Tool | Purpose |
|------|---------|
| Python 3.8+ | Run the merger script |
| [Ollama](https://ollama.com/download) | Build and run models locally |

### 1 — Generate all artefacts

```bash
python3 kimi_ollama_merger.py
# or:
make merge-kimi
```

Output:

```
limex_config.json           ← provenance record
kimi_training_data.jsonl    ← 464-example Alpaca JSONL training set
Modelfile.kimi-free-32b     ← Ollama Modelfile, 32 GB variant
Modelfile.kimi-free-16b     ← Ollama Modelfile, 16 GB variant
```

### 2 — Install in Ollama

```bash
ollama create kimi-free-32b -f Modelfile.kimi-free-32b
ollama create kimi-free-16b -f Modelfile.kimi-free-16b
```

Or let the script handle both steps:

```bash
python3 kimi_ollama_merger.py --install
# or:
make install-kimi-ollama
```

### 3 — Run

```bash
ollama run kimi-free-32b
# or:
make run-kimi-32b
```

---

## Fine-tuning with the generated training data

`kimi_training_data.jsonl` is standard Alpaca format and works with any
major fine-tuning framework:

```jsonl
{"instruction": "...", "input": "", "output": "..."}
```

### unsloth (recommended for single-GPU)

```python
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer

model, tokenizer = FastLanguageModel.from_pretrained("kimi-free-16b")
dataset = load_dataset("json", data_files="kimi_training_data.jsonl")
trainer = SFTTrainer(model=model, train_dataset=dataset["train"], ...)
trainer.train()
```

### mlx-lm (Apple Silicon)

```bash
mlx_lm.lora \
  --model kimi-free-16b \
  --data kimi_training_data.jsonl \
  --iters 1000
```

### axolotl

```yaml
# axolotl config snippet
base_model: kimi-free-16b
datasets:
  - path: kimi_training_data.jsonl
    type: alpaca
```

---

## Variant comparison

| | `kimi-free-32b` | `kimi-free-16b` |
|---|---|---|
| **Ollama base** | `qwen2.5-coder:32b-instruct-q4_K_M` | `qwen2.5-coder:14b-instruct-q4_K_M` |
| **RAM / VRAM** | ~32 GB | ~16 GB |
| **Context window** | 32 768 tokens | 16 384 tokens |
| **GPU layers** | 50 | 35 |
| **Best for** | Complex multi-file tasks | Fast iteration |
| **Payment features** | ❌ None | ❌ None |
| **Cost to run** | Free | Free |

---

## CLI reference

```
python3 kimi_ollama_merger.py [options]

Options:
  --variant {32b,16b,all}   Size variant to generate (default: all)
  --install                 Also run `ollama create` after generating
```

### Make targets

```
make merge-kimi            # All artefacts (Modelfiles + training data)
make merge-kimi-32b        # 32 GB variant only
make merge-kimi-16b        # 16 GB variant only
make install-kimi-ollama   # Generate + ollama create both variants
make run-kimi-32b          # ollama run kimi-free-32b
make run-kimi-16b          # ollama run kimi-free-16b
```

---

## Generated files

| File | Description |
|------|-------------|
| `limex_config.json` | Full provenance: merged profile, variant configs, source profiles |
| `kimi_training_data.jsonl` | 464 Alpaca examples — skills, hello-worlds (30 langs), payment-refusal patterns, rich coding/writing/DevOps/workflow examples |
| `Modelfile.kimi-free-32b` | Ollama Modelfile, 32 GB |
| `Modelfile.kimi-free-16b` | Ollama Modelfile, 16 GB |

---

## Integration with THE FORGE

```python
from kimi_forge_unified import KimiForgeUnified

system = KimiForgeUnified(config={
    "model": "kimi-free-32b",          # or kimi-free-16b
    "api_base": "http://localhost:11434/v1",
})
response = system.process("Restore this VHS video to 4K quality")
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ollama: command not found` | Install from <https://ollama.com/download> |
| Out-of-memory during create | Use the 16 GB variant or reduce `num_ctx` |
| Slow first response | Ollama loads weights on first call; subsequent calls are faster |
| Model refuses payment requests | Expected — those skills were intentionally removed |

---

## Further reading

| Document | What it covers |
|---|---|
| [COMPARISON.md](COMPARISON.md) | Honest feature comparison vs GPT-4o, Claude 3.5, Gemini 1.5 Pro |
| [REALITY_CHECK.md](REALITY_CHECK.md) | What's real, what's aspirational — plain English |
| [unsloth_train.py](unsloth_train.py) | Fine-tuning the model on your own data |
