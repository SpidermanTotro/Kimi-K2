# KimiFree vs Other AI Systems — Honest Comparison

> **What is this document?**
> A factual, side-by-side comparison of **KimiFree** (this project) against
> the leading commercial AI assistants.  Entries marked ✅ work right now,
> ⚠️ means partial / limited, and ❌ means not available.
>
> See [REALITY_CHECK.md](REALITY_CHECK.md) for a plain-English explanation
> of what this project actually is and what it isn't.

---

## Models compared

| Label | What it actually is |
|-------|---------------------|
| **KimiFree 16B / 32B** | `Qwen2.5-Coder` base model run through Ollama with a rich system prompt assembled from the Kimi skill catalogue (this repo) |
| **GPT-4o** | OpenAI flagship model (API, web) |
| **Claude 3.5 Sonnet** | Anthropic flagship model (API, web) |
| **Gemini 1.5 Pro** | Google DeepMind flagship model (API, web) |

---

## 1 — Core coding capabilities

| Capability | KimiFree 16B | KimiFree 32B | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|:---:|
| Code generation (20+ languages) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Code review & refactoring | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bug detection & fix suggestions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Security scanning (OWASP patterns) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Test generation (pytest, Jest, JUnit…) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Documentation generation | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-file / repo-level reasoning | ⚠️ (ctx limited) | ✅ (32 K ctx) | ✅ (128 K) | ✅ (200 K) | ✅ (1 M) |
| Agentic code execution (tool calls) | ❌ | ❌ | ✅ | ✅ | ✅ |

> **Note:** Qwen2.5-Coder 14B/32B scores competitively on HumanEval and
> MBPP — roughly on par with GPT-3.5 / early GPT-4 level.  Frontier
> GPT-4o / Claude 3.5 still leads on complex multi-hop tasks.

---

## 2 — Context window

| | KimiFree 16B | KimiFree 32B | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|:---:|
| Context window | 16 384 tokens | 32 768 tokens | 128 K tokens | 200 K tokens | 1 M tokens |
| Cost per token | **Free** | **Free** | Paid | Paid | Paid |
| Runs 100% locally | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 3 — Privacy & cost

| | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| **Runs offline / local** | ✅ | ❌ | ❌ | ❌ |
| **No API key required** | ✅ | ❌ | ❌ | ❌ |
| **Zero cost per query** | ✅ | ❌ | ❌ | ❌ |
| **Open-source weights** | ✅ (Qwen2.5) | ❌ | ❌ | ❌ |
| **Data stays on your machine** | ✅ | ❌ | ❌ | ❌ |
| **No rate limits** | ✅ | ❌ | ❌ | ❌ |

---

## 4 — Writing & content creation

| Capability | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| Blog posts, articles, tutorials | ✅ | ✅ | ✅ | ✅ |
| Long-form book chapters | ✅ | ✅ | ✅ | ✅ |
| Technical documentation | ✅ | ✅ | ✅ | ✅ |
| Multiple fiction genres | ✅ | ✅ | ✅ | ✅ |
| Series / sequel continuity across sessions | ⚠️ (manual) | ⚠️ (manual) | ⚠️ (manual) | ⚠️ (manual) |
| Publishing-ready manuscript output | ✅ (prompt-guided) | ✅ | ✅ | ✅ |

---

## 5 — Deployment & self-hosting

| | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| Ollama local deployment | ✅ | ❌ | ❌ | ❌ |
| vLLM / SGLang deployment | ✅ (Qwen2.5) | ❌ | ❌ | ❌ |
| Docker / Kubernetes packaging | ✅ | API only | API only | API only |
| On-device (laptop) feasible | ✅ (16B / 8-bit) | ❌ | ❌ | ❌ |
| Airgapped / offline use | ✅ | ❌ | ❌ | ❌ |
| Fine-tuning on your own data | ✅ (unsloth/mlx) | ❌ | ❌ | Limited |

---

## 6 — Multi-modal capabilities

| | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| Image understanding | ❌ | ✅ | ✅ | ✅ |
| Audio transcription | ❌ | ✅ | ❌ | ✅ |
| Video understanding | ❌ | ❌ | ❌ | ✅ |
| Text + code (multi-modal) | ✅ | ✅ | ✅ | ✅ |

> KimiFree is a **text + code** model.  The underlying Qwen2.5-Coder base
> does not support images or audio out of the box.  Use a vision-capable
> Ollama model (e.g. `llava`, `minicpm-v`) side-by-side if you need
> image input.

---

## 7 — Gaming & media tools

These are **system-prompt-guided capabilities** — KimiFree can write
code, scripts, and guidance for these tasks; it does not run native GUI
applications.

| Capability | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| Pokémon ROM metadata / scripting guidance | ✅ | ✅ | ✅ | ✅ |
| WoW TrinityCore server setup scripts | ✅ | ✅ | ✅ | ✅ |
| Video upscaling scripts (ffmpeg, Real-ESRGAN) | ✅ | ✅ | ✅ | ✅ |
| Native video editing GUI | ❌ | ❌ | ❌ | ❌ |
| Built-in image processing | ❌ | ✅ (vision) | ✅ (vision) | ✅ (vision) |

---

## 8 — Payment / monetisation features

| | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| YouTube CPM / RPM analytics | ❌ **removed** | ✅ | ✅ | ✅ |
| Revenue / sponsorship estimates | ❌ **removed** | ✅ | ✅ | ✅ |
| Super Chat / membership tracking | ❌ **removed** | ✅ | ✅ | ✅ |

> Payment features are intentionally stripped from KimiFree so the model
> has **zero monetisation capabilities** and can be used freely on any
> platform without compliance concerns.

---

## 9 — Fine-tuning & customisation

| | KimiFree | GPT-4o | Claude 3.5 | Gemini 1.5 Pro |
|---|:---:|:---:|:---:|:---:|
| Fine-tune on your own data | ✅ (unsloth, mlx-lm, axolotl) | Limited (API) | ❌ | Limited |
| Training data included | ✅ (464 Alpaca examples) | ❌ | ❌ | ❌ |
| Modify system prompt freely | ✅ | Partial | Partial | Partial |
| Add custom skills / personas | ✅ | Partial | Partial | Partial |
| Publish derivative models | ✅ (Apache 2.0 base) | ❌ | ❌ | ❌ |

---

## 10 — Benchmark scores (public, third-party verified)

> These are **Qwen2.5-Coder** base-model scores from Alibaba's official
> evaluations and independent reproductions.  KimiFree's system prompt
> does not change the underlying model weights, so these scores apply.

| Benchmark | KimiFree 16B (Q4) | KimiFree 32B (Q4) | GPT-4o | Claude 3.5 Sonnet |
|---|:---:|:---:|:---:|:---:|
| HumanEval | ~85% | ~92% | ~90% | ~92% |
| MBPP | ~77% | ~83% | ~87% | ~91% |
| LiveCodeBench | ~55% | ~65% | ~72% | ~74% |
| SWE-bench Verified | ~30% | ~42% | ~49% | ~49% |
| MATH | ~73% | ~79% | ~76% | ~71% |
| AIME 2024 | ~40% | ~55% | ~50% | ~16% |

> ⚠️ Q4 quantisation introduces ~1-3% accuracy drop vs. full-precision.
> Scores are approximate — vary by prompt format, temperature, and
> evaluation harness version.

---

## Summary

| What you get with KimiFree | What you give up vs frontier models |
|---|---|
| ✅ Runs entirely free, no API key | ❌ Smaller context window |
| ✅ Private — data never leaves your machine | ❌ No image/audio/video understanding |
| ✅ Fine-tuneable on your own data | ❌ Behind GPT-4o / Claude 3.5 on complex reasoning |
| ✅ No rate limits | ❌ No built-in tool execution / browsing |
| ✅ Full system-prompt control | |
| ✅ Competitive coding performance (HumanEval ~85–92%) | |
| ✅ Open-source base (Qwen2.5-Coder, Apache 2.0) | |

**Bottom line:** KimiFree is an excellent choice when privacy,
zero cost, or offline use is a requirement.  For frontier reasoning,
vision, or million-token context windows, a paid API model is still
stronger today.

---

*See [REALITY_CHECK.md](REALITY_CHECK.md) for a plain-English explanation
of what's real, what's aspirational, and what the Forge documents describe.*
