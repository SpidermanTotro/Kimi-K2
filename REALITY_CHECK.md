# Reality Check — What Is This Project, Actually?

> **The short answer:** This is a real, working tool that wraps the open-source
> `Qwen2.5-Coder` language model in an Ollama Modelfile with a comprehensive
> system prompt derived from the Kimi K2 / FORGE skill catalogue.
> It produces a local, free, privacy-preserving coding assistant.
>
> Some of the surrounding documentation is aspirational / creative writing.
> This document tells you clearly which is which.

---

## ✅ What is genuinely real and working right now

### The merger pipeline (`kimi_ollama_merger.py`)
- **406 skills** catalogued from `docs/ALL_SKILLS.md` across 12 categories
- **9 payment skills** stripped (CPM, RPM, revenue estimates, etc.)
- **30 programming languages** covered
- **464 Alpaca-format training examples** in `kimi_training_data.jsonl`
- **Two Ollama Modelfiles** generated: `Modelfile.kimi-free-32b` and `Modelfile.kimi-free-16b`
- **52 passing unit tests** (`test_kimi_ollama_merger.py`)
- Run it: `python3 kimi_ollama_merger.py`

### The Ollama models
- Based on `qwen2.5-coder:32b-instruct-q4_K_M` and `qwen2.5-coder:14b-instruct-q4_K_M`
- These are **real, downloadable, open-source models** from Alibaba Cloud
- After running `ollama create kimi-free-16b -f Modelfile.kimi-free-16b` you get
  a real local model that answers coding, writing, and DevOps questions for free
- Context window: 16 384 tokens (16B) / 32 768 tokens (32B)

### The fine-tuning helper (`unsloth_train.py`)
- Real Python script that calls the real `unsloth` + `trl` + `transformers` stack
- Requires a GPU with ~16 GB VRAM (16B model)
- The training data (`kimi_training_data.jsonl`) is real Alpaca JSONL

### The build system and tests
- `make merge-kimi` / `make test-merger` both work
- `python3 -m pytest test_kimi_ollama_merger.py` — 52/52 pass

---

## ⚠️ What is real but overstated in the docs

### "1 Trillion parameters"
The Kimi K2 model from Moonshot AI is a **real 1-trillion-parameter MoE model**.
*However*, KimiFree 16B and 32B are **Qwen2.5-Coder 14B / 32B** — which are
14 billion and 32 billion parameters respectively.
The 1T figure applies to the upstream Kimi K2 model, not to the local Ollama
variants this project creates.

### "431K+ lines of code / 6,100+ lines documentation"
The documentation figures count across the entire FORGE project history,
including aspirational design documents. The actual executable Python in this
repo is around 2,000–3,000 lines.

### "VHS → 8K restoration", "Pokémon upscaling", "Video editing"
KimiFree can **write scripts and guidance** for these tasks using Real-ESRGAN,
ffmpeg, GIMP scripting, etc.  It does **not** execute them natively — there is
no built-in video encoder or image processing engine in the model itself.

### "Never-reset memory / living character worlds"
These are features described in the FORGE ecosystem design documents.
The current Ollama deployment has standard context-window memory (16 K / 32 K
tokens). Persistent cross-session memory would require an external vector
database (e.g. Chroma, Weaviate) — not included yet.

### "128K context window"
The upstream Kimi K2 model supports 128 K tokens.  The local Ollama variants
are capped at 16 K / 32 K to fit consumer hardware.

---

## ❌ What is aspirational / not yet implemented

| Claim in docs | Reality |
|---|---|
| Real-time neural video upscaling | Script guidance only; no built-in encoder |
| Native image generation | Not implemented; requires separate Stable Diffusion setup |
| Automatic sequel detection | Prompt-guided capability, not a dedicated ML pipeline |
| Cross-session persistent memory | Requires external vector DB; not wired up yet |
| WoW server automation GUI | Scripts only; no dedicated GUI application |
| Pokémon sprite neural upscaling at runtime | Script + Real-ESRGAN guidance; no embedded model |
| Emotional climate / cosmic layer | Creative concept in ecosystem docs; not an implemented system |
| BookForge / ShadowForge / Weather Forge UI | Described in design docs; not built as running apps |
| 10M+ movie database | Mentioned in FORGE design docs; no database included here |
| "Bootable Linux OS builder" | Not implemented in this repository |

---

## What the FORGE / Kimi documentation is

The `docs/` folder contains **design documents and vision files** written
to describe the full aspirational FORGE AI ecosystem.  They are detailed,
well-structured, and technically coherent — but they describe a target
state, not the current executable state of this repository.

Think of them as a product specification / roadmap, not an installation
manual.

---

## How to verify for yourself

```bash
# 1. Run the merger and see what it actually produces
python3 kimi_ollama_merger.py

# 2. Run the tests — all 52 should pass
python3 -m pytest test_kimi_ollama_merger.py -v

# 3. Look at the real generated Modelfile
cat Modelfile.kimi-free-16b | head -30

# 4. Check the training data
python3 unsloth_train.py --stats

# 5. Install in Ollama (requires Ollama to be installed)
ollama create kimi-free-16b -f Modelfile.kimi-free-16b
ollama run kimi-free-16b
# Then ask: "Write a FastAPI CRUD endpoint"
```

---

## What makes this project genuinely useful

1. **Free, private, local AI coding assistant** — no API key, no cloud, no cost
2. **Thoughtfully curated system prompt** — 406 skills across 12 categories tell
   the model exactly what it's good at
3. **Payment-free by design** — 9 monetisation skills removed, so it can be
   deployed anywhere without compliance risk
4. **Fine-tunable** — 464-example training dataset included; adapt the model
   to your specific codebase / domain
5. **Open workflow** — regenerate everything with one command; extend the skill
   catalogue in Python

---

## Further reading

| Document | What it covers |
|---|---|
| [COMPARISON.md](COMPARISON.md) | Side-by-side feature table vs GPT-4o, Claude, Gemini |
| [KIMI_OLLAMA_MERGER.md](KIMI_OLLAMA_MERGER.md) | How to install and run the local models |
| [unsloth_train.py](unsloth_train.py) | Fine-tuning the model on your own data |
| [docs/SKILLS_MATRIX.md](docs/SKILLS_MATRIX.md) | Full 365+ skill catalogue |
| [docs/ROADMAP.md](docs/vision_and_roadmap.md) | Long-term vision for the FORGE ecosystem |

---

*Last updated: March 2026*
