# Kimi Coding Model Merger — Ollama / limex Guide

> **TL;DR** — This tool strips the coding capabilities from **Kimi**,
> **Kimi 2**, and **Kimi 2.5**, merges them into a single unified system
> prompt, and generates two ready-to-use [Ollama](https://ollama.com)
> model configurations:
>
> | Variant | RAM target | Ollama model name |
> |---------|-----------|-------------------|
> | 32 GB   | 32 GB     | `kimi-coding-32b` |
> | 16 GB   | 16 GB     | `kimi-coding-16b` |

---

## What is limex?

**limex** (**L**ightweight **I**ntegrated **M**odel **EX**change) is the
small framework used here to:

1. Define per-generation coding-skill profiles (strengths, languages,
   context window).
2. Deduplicate and union those profiles into one merged configuration.
3. Emit Ollama `Modelfile`s and a `limex_config.json` provenance record
   from that merged configuration.

---

## Quick start

### Prerequisites

| Tool | Purpose |
|------|---------|
| Python 3.8+ | Run the merger script |
| [Ollama](https://ollama.com/download) | Build and run the model locally |

### 1 — Generate Ollama artefacts

```bash
python3 kimi_ollama_merger.py
# or via Make:
make merge-kimi
```

This produces three files:

```
limex_config.json          ← full provenance record
Modelfile.kimi-coding-32b  ← Ollama Modelfile, 32 GB variant
Modelfile.kimi-coding-16b  ← Ollama Modelfile, 16 GB variant
```

### 2 — Install one or both models into Ollama

```bash
# 32 GB variant (requires ~20 GB disk + 32 GB RAM/VRAM)
ollama create kimi-coding-32b -f Modelfile.kimi-coding-32b

# 16 GB variant (requires ~10 GB disk + 16 GB RAM/VRAM)
ollama create kimi-coding-16b -f Modelfile.kimi-coding-16b
```

Or let the script do it for you:

```bash
python3 kimi_ollama_merger.py --install
# or:
make install-kimi-ollama
```

### 3 — Run the model

```bash
ollama run kimi-coding-32b
# or:
ollama run kimi-coding-16b
```

---

## Choosing a variant

| | `kimi-coding-32b` | `kimi-coding-16b` |
|---|---|---|
| **Ollama base** | `qwen2.5-coder:32b-instruct-q4_K_M` | `qwen2.5-coder:14b-instruct-q4_K_M` |
| **RAM / VRAM** | ~32 GB | ~16 GB |
| **Context window** | 32 768 tokens | 16 384 tokens |
| **GPU layers** | 50 | 35 |
| **Best for** | Complex, multi-file tasks | Fast iteration on smaller tasks |

---

## Merged coding strengths

The merged model inherits **all** strengths from every Kimi generation:

| Source | Highlights |
|--------|-----------|
| **Kimi v1** | Python scripting, REST API design, SQL, basic web |
| **Kimi 2** | Full-stack (React/FastAPI), C/C++/Rust, security, CI/CD |
| **Kimi 2.5** | Agentic SWE, long-context (>100 K tokens), TDD, IaC |

**Supported languages** (19 total):
`bash` · `c` · `cpp` · `css` · `dockerfile` · `go` · `graphql` · `hcl` ·
`html` · `java` · `javascript` · `kotlin` · `python` · `rust` · `sql` ·
`swift` · `terraform` · `typescript` · `yaml`

---

## CLI reference

```
python3 kimi_ollama_merger.py [options]

Options:
  --variant {32b,16b,all}   Which size variant to generate (default: all)
  --install                 After generating, run `ollama create` locally
```

### Make targets

```
make merge-kimi            # Generate all artefacts
make merge-kimi-32b        # 32 GB Modelfile only
make merge-kimi-16b        # 16 GB Modelfile only
make install-kimi-ollama   # Generate + ollama create both variants
make run-kimi-32b          # ollama run kimi-coding-32b
make run-kimi-16b          # ollama run kimi-coding-16b
```

---

## Generated files

### `limex_config.json`

Machine-readable provenance record.  Contains the full merged profile, per-
generation source profiles, and variant deployment parameters.  Use this in
CI to verify that the Modelfiles were generated from the expected sources.

### `Modelfile.kimi-coding-32b` / `Modelfile.kimi-coding-16b`

Standard Ollama `Modelfile`s.  You can edit them directly to:

- Swap the `FROM` base (e.g. to a locally downloaded GGUF file).
- Adjust `PARAMETER num_ctx` for your available memory.
- Add `PARAMETER num_gpu 0` to force CPU-only inference.

---

## Integration with THE FORGE

The merged KimiCoder model is designed to complement the existing
**THE FORGE ❤️ KIMI K2** integration:

```python
from kimi_forge_unified import KimiForgeUnified

# Point the unified system at the local Ollama endpoint
system = KimiForgeUnified(config={
    "model": "kimi-coding-32b",   # or kimi-coding-16b
    "api_base": "http://localhost:11434/v1",
})
response = system.process("Refactor this Python module for async I/O")
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ollama: command not found` | Install Ollama from <https://ollama.com/download> |
| Out-of-memory during `ollama create` | Use the 16 GB variant or reduce `num_ctx` |
| Slow first response | Ollama is loading model weights; subsequent calls are faster |
| Wrong chat format | Edit `TEMPLATE` in the Modelfile to match your base model |
