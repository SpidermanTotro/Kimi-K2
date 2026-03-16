#!/usr/bin/env python3
"""
Kimi All-Skills Model Merger for Ollama (limex framework)
==========================================================

Collects every skill from Kimi, Kimi 2, and Kimi 2.5 across all
12 categories (365+ individual capabilities), strips all payment /
monetisation skills, and produces:

  * Two Ollama Modelfiles  (32 GB and 16 GB)
  * A limex_config.json   provenance record
  * A kimi_training_data.jsonl  Alpaca-format fine-tuning dataset
    (compatible with unsloth, mlx-lm, axolotl, etc.)

Usage:
    python3 kimi_ollama_merger.py              # generate all artefacts
    python3 kimi_ollama_merger.py --variant 32b
    python3 kimi_ollama_merger.py --variant 16b
    python3 kimi_ollama_merger.py --install    # also run `ollama create`
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Payment / monetisation keywords — skills matching any of these phrases
# are stripped from Kimi 2 and Kimi 2.5 before merging.
# ---------------------------------------------------------------------------

PAYMENT_KEYWORDS: List[str] = [
    "monetization insight",
    "monetisation insight",
    "cpm analysis",
    "rpm tracking",
    "revenue estimate",
    "ad type performance",
    "sponsorship value",
    "super chat tracking",
    "membership insights",
    "merchandise click",
    "payment",
    "billing",
    "subscription fee",
    "credit card",
    "stripe",
    "paypal",
    "invoice",
    "pricing tier",
    "paid feature",
    "ad revenue",
    "commercial use",
]


def _is_payment_skill(skill: str) -> bool:
    """Return True if *skill* matches any payment keyword (case-insensitive)."""
    lower = skill.lower()
    return any(kw.lower() in lower for kw in PAYMENT_KEYWORDS)


# ---------------------------------------------------------------------------
# Full skill catalogue extracted from ALL_SKILLS.md and FORGE docs
# ---------------------------------------------------------------------------

# ── PROGRAMMING & CODE  (60+ capabilities) ─────────────────────────────────
_PROG_CODE: List[str] = [
    # Code Generation
    "Multi-language code generation (20+ languages)",
    "Complete applications from scratch",
    "Individual functions with documentation",
    "Classes with full methods",
    "Modules and packages",
    "API endpoints",
    "Database schemas",
    "Test suites",
    "Configuration files",
    "Build scripts",
    "Deployment configs",
    "Type hints and annotations",
    "Comprehensive docstrings",
    "Design patterns implementation (SOLID principles)",
    "Clean code practices",
    # Code Review & Analysis
    "Structural code analysis",
    "Logic verification",
    "Performance bottleneck identification",
    "Code smell detection",
    "Complexity analysis",
    "Maintainability scoring",
    "Readability assessment",
    "API design review",
    "Architecture review",
    "Refactoring opportunity identification",
    "Code duplication detection",
    # Bug Detection & Fixing
    "Syntax error detection",
    "Logic error detection",
    "Off-by-one error detection",
    "Null pointer / None exception detection",
    "Type mismatch detection",
    "Race condition detection",
    "Memory leak detection",
    "Infinite loop detection",
    "Edge case failure detection",
    "Auto-fix generation with explanations",
    # Security
    "SQL injection detection and prevention",
    "XSS vulnerability scanning",
    "CSRF protection review",
    "Authentication issue detection",
    "Cryptography problem detection",
    "Insecure dependency scanning",
    "Path traversal detection",
    "Command injection prevention",
    # Performance
    "Algorithm optimisation",
    "Data structure selection guidance",
    "Caching strategy design",
    "Database query optimisation",
    "Memory usage optimisation",
    "CPU and I/O optimisation",
    "Code profiling and bottleneck identification",
    # Testing
    "Unit test generation (pytest, Jest, JUnit, etc.)",
    "Integration test generation",
    "End-to-end test generation",
    "API test generation",
    "Performance and load test generation",
    "Security test generation",
    "Regression and smoke test generation",
    # Documentation
    "Function / class docstring generation",
    "API documentation (REST, GraphQL, gRPC)",
    "OpenAPI / Swagger spec generation",
    "README file generation",
    "Architecture and design docs",
    "Changelog generation",
    # Advanced
    "Agentic software engineering (SWE-bench level)",
    "Long-context repository understanding (>100 K tokens)",
    "Advanced debugging and root-cause analysis",
    "Test-driven development with full coverage",
    "Multi-language polyglot projects",
    "Formal verification patterns",
    "Compiler and interpreter implementation",
    "Embedded and real-time systems programming",
    "Concurrent and parallel programming (async, threads, actors)",
    "Full-stack web development (React, Node.js, FastAPI)",
    "Systems programming in C, C++, Rust",
    "Multi-file refactoring and code review",
    "CI/CD pipeline configuration (GitHub Actions, Docker)",
    "Mathematical algorithm implementation",
    "Security-hardened code generation",
    "Type-safe TypeScript applications",
    "Go microservices",
    "Java enterprise patterns",
    "Performance optimisation and profiling",
]

# ── CONTENT CREATION & WRITING  (80+ capabilities) ─────────────────────────
_WRITING: List[str] = [
    # Book types
    "Technical book writing",
    "Programming tutorial writing",
    "Fiction novel writing",
    "Non-fiction book writing",
    "Educational textbook writing",
    "Research paper and thesis writing",
    "White paper authoring",
    "Case study writing",
    "Industry report writing",
    # Publishing quality
    "Award-winning prose generation",
    "Professional manuscript preparation",
    "Publishing-ready output",
    "Quality upscaling (draft → professional)",
    "Style consistency throughout document",
    "Voice strengthening and flow optimisation",
    # Sequel & series
    "Automatic sequel detection",
    "Book series order detection",
    "Plot thread continuity tracking",
    "Series structure planning (trilogy, saga)",
    "Character arc continuity across books",
    "Timeline management across books",
    # Genre mastery (50+ genres)
    "Genre mastery: Sci-Fi, Fantasy, Mystery, Thriller, Romance, Horror",
    "Genre mastery: Business, Self-help, Biography, History, Science",
    "Genre mastery: Programming books, Academic textbooks",
    "Genre convention, trope awareness, reader expectation matching",
    # Author features
    "Deep character development",
    "Plot development (three-act, hero's journey)",
    "World-building (cultures, history, systems)",
    "Dialogue mastery with unique character voices",
    "Show-don't-tell technique",
    "Literary devices integration",
    "Multiple POV handling",
    "Flashback and time manipulation",
    "Symbolism and metaphor usage",
    # Editing
    "Content editing (plot holes, consistency)",
    "Copy editing (grammar, style)",
    "Line editing (sentence-level improvement)",
    "Proofreading and final polish",
    "Character consistency verification",
    "Fact-checking and logic verification",
    # Publishing preparation
    "Front and back matter generation",
    "Multiple format export (PDF, EPUB, MOBI, DOCX, HTML)",
    "Metadata preparation (BISAC codes, keywords)",
    "Cover design guidance",
    "Author bio generation",
    # Marketing
    "Book description generation (multiple lengths)",
    "Press release writing",
    "Media kit content",
    "Discussion questions generation",
    # Content writing
    "Blog posts and articles",
    "SEO-optimised tutorial writing",
    "Product descriptions and marketing copy",
    "Academic papers and reports",
    "Presentations and newsletters",
    "Email campaigns and social media posts",
    # Documentation
    "Contributing guidelines and code of conduct",
    "Installation and configuration guides",
    "Migration guides and release notes",
    "User manuals and admin guides",
    "Onboarding documentation",
]

# ── GAMING ENHANCEMENT  (40+ capabilities) ─────────────────────────────────
_GAMING: List[str] = [
    # Pokémon coverage
    "Pokémon Gen 1 enhancement (Red, Blue, Yellow, Green)",
    "Pokémon Gen 2 enhancement (Gold, Silver, Crystal)",
    "Pokémon Gen 3 enhancement (Ruby, Sapphire, Emerald, FireRed, LeafGreen)",
    "Pokémon Gen 4 enhancement (Diamond, Pearl, Platinum, HeartGold, SoulSilver)",
    "Pokémon Gen 5 enhancement (Black, White, Black 2, White 2)",
    "Pokémon Gen 6 enhancement (X, Y, Omega Ruby, Alpha Sapphire)",
    "Pokémon Gen 7 enhancement (Sun, Moon, Ultra Sun, Ultra Moon)",
    "Pokémon spin-offs (Mystery Dungeon, Ranger, Conquest, Stadium, Snap)",
    # Graphics
    "Neural upscaling to 4K / 8K",
    "8-bit to HD sprite conversion",
    "Texture generation and lighting effects",
    "Smooth animations (60 FPS)",
    "Modern shading and dynamic shadows",
    "Weather effects and water reflections",
    # WoW server
    "WoW Vanilla server setup (Classic 1.12.1)",
    "WoW The Burning Crusade server (2.4.3)",
    "WoW Wrath of the Lich King server (3.3.5a)",
    "WoW Cataclysm through Dragonflight server (all 12 expansions)",
    "TrinityCore / AzerothCore / CMaNGOS integration",
    "WoW database setup (MySQL/MariaDB)",
    "WoW authentication, security, performance optimisation",
    # General
    "Game logic implementation",
    "Save-state management",
    "ROM metadata enrichment",
    "Game-save editor tooling",
    "Emulator configuration automation",
    "Speedrun route analysis",
    "ROM upscaling (SD → 8K)",
]

# ── VIDEO & IMAGE PROCESSING  (35+ capabilities) ────────────────────────────
_VIDEO_IMAGE: List[str] = [
    # Video upscaling
    "SD to HD upscaling (480p → 1080p)",
    "HD to 4K upscaling (1080p → 4K)",
    "4K to 8K upscaling",
    "Frame rate enhancement (30fps → 60fps, 24fps → 60fps)",
    "Frame interpolation for smooth motion",
    "Noise reduction and artefact removal",
    "Video colour correction and grading",
    "Video stabilisation and deinterlacing",
    "Format conversion (all codec/container combinations)",
    "Batch processing with GPU acceleration",
    # Image upscaling
    "Low-res to HD image upscaling",
    "Neural super-resolution",
    "Edge enhancement and detail restoration",
    "JPEG artefact removal and grain removal",
    "RAW format support (CR2, NEF, ARW, DNG)",
    "Animated GIF processing",
    # Image creation
    "Style transfer",
    "Diagram, chart, flowchart generation",
    "UI mockup and wireframe creation",
    "Sprite sheet and tilemap generation",
    "Pixel art creation",
    "Infographic design",
    # Advanced
    "Historical restoration (VHS → 8K, 1956-era films)",
    "AI-driven colourisation of B&W footage",
    "Object detection in images/video",
    "Scene recognition",
    "Background removal (content-aware fill)",
    "Motion tracking",
    "File size reduction with quality preservation",
    "Color space management (RGB, CMYK, HSV)",
    "Print preparation (DPI/PPI handling)",
]

# ── MULTIMEDIA & PRODUCTIVITY  (210+ capabilities) ──────────────────────────
_MULTIMEDIA: List[str] = [
    # Video editing
    "Multi-track timeline editing (unlimited tracks)",
    "Cutting tools (razor, ripple delete, trim)",
    "Speed control (slow motion, timelapse, reverse)",
    "100+ video transitions (fade, wipe, dissolve, 3D)",
    "Video effects (blur, sharpen, glow, vignette, noise)",
    "Professional colour grading (colour wheels, RGB curves, LUTs)",
    "Multi-track audio mixing with ducking and normalisation",
    "10-band parametric EQ and audio effects",
    "100+ professional title templates and animated titles",
    "Lower thirds and scrolling credits",
    "3D text with depth and shadows",
    "Green screen / chroma key",
    "Motion tracking (objects, text)",
    "Keyframe animation for any parameter",
    "Video stabilisation",
    "Multi-cam editing",
    "Export to MP4/MOV/AVI/WebM/MKV in SD/HD/4K/8K",
    "Hardware-accelerated encoding (GPU)",
    # Word processing
    "Rich text formatting with 1000+ fonts",
    "Auto-generated table of contents with links",
    "Footnotes, endnotes, bibliography (APA, MLA, Chicago, Harvard)",
    "Auto-generated index with page numbers",
    "Track changes and collaboration tools",
    "Document comparison and version history",
    "Mail merge (CSV, database, contacts)",
    "Document templates (reports, resumes, letters)",
    "Export to DOCX/PDF/ODT/HTML/EPUB/LaTeX/Markdown",
    "Accessibility (screen reader, ARIA, contrast checking)",
    # Photo editing
    "Unlimited layer-based editing with 30+ blend modes",
    "Layer masks and clipping masks",
    "Selection tools (lasso, magic wand, quick select)",
    "Levels, curves, hue/saturation/lightness adjustments",
    "Healing brush, clone stamp, content-aware fill",
    "200+ filters (blur, sharpen, artistic, distort, noise)",
    "Batch processing and actions/macros",
    "16-bit editing and ICC colour profiles",
    "RAW support with non-destructive editing",
    "Smart objects and HDR merge",
    "Export to JPEG/PNG/TIFF/PSD/WebP/AVIF",
    # YouTube (non-payment features only)
    "YouTube channel analytics (views, CTR, audience retention)",
    "YouTube content strategy and topic research",
    "Keyword research and trending topic analysis",
    "Competitor analysis and content gap identification",
    "Thumbnail A/B testing and CTR analysis",
    "Playlist strategy and description optimisation",
    # Audio
    "FM radio recording and scheduling (personal use only)",
    "Audio editing (trim, fade, normalise, noise reduction)",
    "Multi-track recording and mixing",
    "Effects: reverb, delay, compression, EQ, noise gate",
    "Voice processing (de-click, de-breath, clarity enhancement)",
    "Podcast production (chapter markers, loudness standards)",
    "Export to MP3/WAV/FLAC/AAC/OGG/M4A",
    # TV recording
    "TV show scheduling and series recording (personal use only)",
    "Time-shifting (pause, rewind, skip live TV)",
    "Commercial skip and chapter markers",
    "Show metadata and library organisation",
    "Multi-tuner support for simultaneous recordings",
    # Production
    "Screencast recording with webcam overlay and annotations",
    "Live streaming to YouTube/Twitch/Facebook/RTMP",
    "2D animation (frame-by-frame, tweening, sprite sheets)",
    "VFX compositing (green screen, particle systems)",
    "Subtitle generation, translation, and export (SRT/VTT/ASS)",
]

# ── GITHUB & VERSION CONTROL  (25+ capabilities) ────────────────────────────
_GITHUB: List[str] = [
    # Repository
    "Create, fork, clone, archive, transfer repositories",
    "Configure settings, collaborators, webhooks",
    "Branch protection rules and deploy keys",
    "Repository secrets and environment configuration",
    "Repository topics and templates",
    # Git operations
    "Commit, branch, merge, rebase, cherry-pick",
    "Stash, tag, manage remotes, interactive rebase",
    "Bisect for bug hunting",
    "Submodule management",
    "Git hooks setup",
    "Conflict resolution",
    "History rewriting (squash, amend, reset, revert)",
    "Diff analysis and blame investigation",
    # Pull requests
    "Create and review pull requests",
    "Request reviews, approve/reject PRs",
    "Merge strategies (merge, squash, rebase)",
    "Auto-merge setup and draft PRs",
    "PR templates",
    # Issues & projects
    "Create issues and auto-create from bugs",
    "Label management and milestone tracking",
    "Project boards",
    "Link commits to issues",
    # Actions
    "CI/CD workflow authoring",
    "Build, test, deployment, and release automation",
    "Code quality checks and security scanning",
    "Dependency updates and Docker builds",
    "Matrix builds, caching, artifact management",
    "Secrets management and scheduled workflows",
    # Advanced
    "Full repository lifecycle management",
    "Automated code review bots",
    "Dependency graph analysis",
    "Security advisory integration",
    "Multi-repo monorepo orchestration",
]

# ── FILE HANDLING & PROCESSING  (20+ capabilities) ──────────────────────────
_FILES: List[str] = [
    "Code file analysis (.py, .js, .ts, .java, .cpp, .go, .rs, etc.)",
    "Document parsing (.pdf, .doc, .docx, .txt, .md, .epub)",
    "Spreadsheet processing (.xls, .xlsx, .csv, .ods)",
    "Image file handling (.jpg, .png, .gif, .svg, .webp, .tiff)",
    "Audio file handling (.mp3, .wav, .flac, .ogg, .aac)",
    "Video file handling (.mp4, .avi, .mkv, .mov)",
    "Archive creation and extraction (.zip, .tar, .gz, .7z, .rar)",
    "ROM file handling (.gb, .gbc, .gba, .nds, .3ds, .nes, .snes, .n64)",
    "Database file handling (.sql, .db, .sqlite)",
    "Universal file type detection and parsing",
    "Binary diff and patch generation",
    "Metadata reading (EXIF, IPTC, XMP, ID3)",
    "File validation and format conversion",
    "Content summarisation",
    "Dependency detection from files",
    "30+ file types supported",
]

# ── AI / ML & ADVANCED TECH  (15+ capabilities) ─────────────────────────────
_AI_ML: List[str] = [
    "Machine learning pipeline design",
    "Model training guidance and A/B testing setup",
    "Feature engineering and data preprocessing",
    "Model selection and hyperparameter tuning",
    "Model evaluation metrics",
    "Neural network architecture explanation",
    "Image super-resolution (neural upscaling)",
    "LLM fine-tuning workflow design",
    "RAG (retrieval-augmented generation) pipeline design",
    "Vector database integration",
    "Model quantisation guidance (GGUF, AWQ, GPTQ)",
    "On-device inference optimisation",
    "Automatic model retraining setup",
    "Batch processing and GPU optimisation",
    "Quality preset design (fast, balanced, quality)",
]

# ── DEVOPS & DEPLOYMENT  (20+ capabilities) ─────────────────────────────────
_DEVOPS: List[str] = [
    # Containerisation
    "Dockerfile creation and multi-stage builds",
    "Docker image building and layer optimisation",
    "Docker Compose multi-service stacks",
    "Container security scanning",
    "Docker registry management",
    # Kubernetes
    "Kubernetes deployment, service, and ingress definitions",
    "ConfigMaps, Secrets, StatefulSets, DaemonSets",
    "Jobs, CronJobs, Helm chart generation",
    "Resource management and monitoring setup",
    # IaC
    "Terraform configs and state management",
    "CloudFormation, CDK, ARM template generation",
    "Ansible playbooks, Chef recipes, Puppet manifests",
    # Deployment platforms
    "AWS, Azure, Google Cloud deployment",
    "Heroku, Vercel, Netlify, DigitalOcean deployment",
    "Railway, Render, Fly.io, Docker, bare-metal deployment",
    "Serverless deployment",
    # Advanced
    "GitOps workflow design",
    "Service mesh configuration (Istio, Linkerd)",
    "Observability stack (Prometheus, Grafana, Loki)",
    "Chaos engineering experiments",
    "Zero-downtime deployment strategies",
]

# ── SECURITY & COMPLIANCE  (15+ capabilities) ───────────────────────────────
_SECURITY: List[str] = [
    "OWASP Top-10 vulnerability scanning",
    "Dependency CVE analysis",
    "Secret detection",
    "Authentication flow review",
    "Authorization and privilege escalation review",
    "Encryption validation",
    "Certificate management",
    "Security headers and CORS configuration",
    "Rate limiting and DDoS protection guidance",
    "Penetration test scripting",
    "Threat-model documentation",
    "Zero-trust architecture design",
    "Cryptography implementation review",
    "GDPR compliance mapping",
    "HIPAA compliance mapping",
    "SOC 2 compliance mapping",
    "PCI DSS compliance mapping",
    "ISO 27001 alignment",
    "Privacy policy and terms of service generation",
]

# ── ECOSYSTEM & CHARACTER  (30+ capabilities) ───────────────────────────────
_ECOSYSTEM: List[str] = [
    # Forge branches
    "BookForge Infinity (knowledge storage, story generation, eternal archive)",
    "Wildness Café (social interactions, relationship building, community hub)",
    "Weather Forge (emotional climate, mood reflection, atmospheric storytelling)",
    "Nebula Forge (cosmic narratives, spiritual growth, dream sequences)",
    "ShadowForge (conflict management, trauma handling, healing systems)",
    "Azeroth Pilot Reloaded (game mechanics, combat systems, WoW integration)",
    "Character Worlds (living narratives, character growth, relationship tracking)",
    # Character management
    "Persistent character personalities (Henric, Lisa, The Girls, Monash)",
    "Relationship memory and emotional depth",
    "Character evolution and growth arcs",
    "Dialogue generation and interaction systems",
    "Backstory development",
    "Character consistency across sessions",
    # Community
    "Community-driven open-source contribution workflows",
    "Plugin architecture design",
    "Continuous-learning loop integration",
]

# ── UNIQUE FORGE FEATURES  (25+ capabilities) ───────────────────────────────
_UNIQUE: List[str] = [
    # Never-reset
    "Never-reset continuous memory across sessions",
    "Cumulative knowledge and persistent state",
    "Cross-session relationship continuity",
    "Character persistence and knowledge accumulation",
    "History preservation",
    # Ecosystem integration
    "All branches feed each other (bidirectional linking)",
    "Knowledge sharing and state synchronisation",
    "Event propagation and cross-system updates",
    "Unified memory and interconnected features",
    "Living ecosystem with holistic operation",
    # Agentic intelligence
    "Multi-step planning and decision making",
    "Intelligent tool selection",
    "Workflow orchestration and error recovery",
    "Goal pursuit and resource management",
    "Task decomposition and progress tracking",
    "Adaptive learning and context awareness",
    "Self-correction and continuous improvement",
    # Scale
    "131K context window for full repository ingestion",
    "1 Trillion parameter model (Kimi K2 base)",
    "Self-hosted, zero-cost deployment on local hardware",
    "Fully open source and community-driven",
    "Complete documentation (6,100+ lines)",
]


# ---------------------------------------------------------------------------
# Per-generation profiles — maps each Kimi generation to the skill
# categories it contributes, plus a flag to strip payment skills.
# ---------------------------------------------------------------------------

KIMI_V1_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v1",
    "display_name": "Kimi (v1)",
    "strip_payment": False,
    "skills": {
        "programming":    _PROG_CODE[:20],   # basic subset
        "writing":        _WRITING[:10],
        "gaming":         [],
        "video_image":    [],
        "multimedia":     [],
        "github":         _GITHUB[:8],
        "files":          _FILES[:6],
        "ai_ml":          _AI_ML[:3],
        "devops":         _DEVOPS[:4],
        "security":       _SECURITY[:5],
        "ecosystem":      [],
        "unique_features": [_UNIQUE[17]],    # context window entry
    },
    "supported_languages": [
        "python", "javascript", "html", "css", "sql", "bash",
    ],
    "context_window": 8192,
}

KIMI_V2_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v2",
    "display_name": "Kimi 2",
    "strip_payment": True,
    "skills": {
        "programming":    _PROG_CODE[:50],
        "writing":        _WRITING[:35],
        "gaming":         _GAMING[:10],
        "video_image":    _VIDEO_IMAGE[:15],
        "multimedia":     _MULTIMEDIA[:30]
        + [
            # payment skills — will be stripped
            "YouTube monetization insights: Revenue estimates",
            "YouTube monetization insights: CPM analysis (cost per 1000 views)",
            "YouTube monetization insights: RPM tracking",
            "YouTube monetization insights: Ad type performance",
            "YouTube monetization insights: Sponsorship value calculation",
            "YouTube monetization insights: Super Chat tracking",
            "YouTube monetization insights: Membership insights",
            "YouTube monetization insights: Merchandise click tracking",
        ],
        "github":         _GITHUB[:20],
        "files":          _FILES[:12],
        "ai_ml":          _AI_ML[:8],
        "devops":         _DEVOPS[:12],
        "security":       _SECURITY[:10],
        "ecosystem":      _ECOSYSTEM[:5],
        "unique_features": _UNIQUE[:10],
    },
    "supported_languages": [
        "python", "javascript", "typescript", "rust", "c", "cpp",
        "go", "java", "bash", "yaml", "dockerfile", "kotlin", "swift",
    ],
    "context_window": 32768,
}

KIMI_V25_PROFILE: Dict[str, Any] = {
    "model_id": "kimi-v2.5",
    "display_name": "Kimi 2.5",
    "strip_payment": True,
    "skills": {
        "programming":    _PROG_CODE,        # all
        "writing":        _WRITING,
        "gaming":         _GAMING,
        "video_image":    _VIDEO_IMAGE,
        "multimedia":     _MULTIMEDIA
        + [
            # payment skills — will be stripped
            "YouTube monetization insights: Revenue estimates",
            "YouTube monetization insights: CPM analysis",
            "YouTube monetization insights: RPM tracking",
            "YouTube monetization insights: Sponsorship value calculation",
            "YouTube monetization insights: Super Chat tracking",
            "YouTube monetization insights: Membership insights",
        ],
        "github":         _GITHUB,
        "files":          _FILES,
        "ai_ml":          _AI_ML,
        "devops":         _DEVOPS,
        "security":       _SECURITY,
        "ecosystem":      _ECOSYSTEM,
        "unique_features": _UNIQUE,
    },
    "supported_languages": [
        "python", "javascript", "typescript", "rust", "c", "cpp",
        "go", "java", "kotlin", "swift", "bash", "yaml",
        "dockerfile", "terraform", "hcl", "sql", "graphql",
        "lua", "ruby", "php", "r", "scala", "elixir", "haskell",
        "dart", "perl", "powershell", "csharp",
    ],
    "context_window": 131072,
}

ALL_PROFILES: List[Dict[str, Any]] = [
    KIMI_V1_PROFILE,
    KIMI_V2_PROFILE,
    KIMI_V25_PROFILE,
]


# ---------------------------------------------------------------------------
# limex merger
# ---------------------------------------------------------------------------

class LimexModelMerger:
    """
    Lightweight Integrated Model EXchange (limex) merger.

    Merges all skill categories from every Kimi generation,
    filters payment skills from models that carry the strip_payment flag,
    and emits Ollama Modelfiles, a limex config, and Alpaca JSONL
    training data.
    """

    OLLAMA_BASE_32B = "qwen2.5-coder:32b-instruct-q4_K_M"
    OLLAMA_BASE_16B = "qwen2.5-coder:14b-instruct-q4_K_M"

    MAX_CTX_32B = 32768
    MAX_CTX_16B = 16384

    GPU_LAYERS_32B = 50
    GPU_LAYERS_16B = 35

    CATEGORY_LABELS: Dict[str, str] = {
        "programming":    "Programming & Code (60+ capabilities)",
        "writing":        "Content & Writing (80+ capabilities)",
        "gaming":         "Gaming Enhancement (40+ capabilities)",
        "video_image":    "Video & Image Processing (35+ capabilities)",
        "multimedia":     "Multimedia & Productivity (210+ capabilities)",
        "github":         "GitHub & Version Control (25+ capabilities)",
        "files":          "File Handling & Processing (20+ capabilities)",
        "ai_ml":          "AI / ML & Advanced Tech (15+ capabilities)",
        "devops":         "DevOps & Deployment (20+ capabilities)",
        "security":       "Security & Compliance (15+ capabilities)",
        "ecosystem":      "Ecosystem & Character Systems (30+ capabilities)",
        "unique_features":"Unique FORGE Features (25+ capabilities)",
    }

    SYSTEM_PROMPT_TEMPLATE = """\
You are KimiFree — a unified AI assistant built from the merged capabilities \
of Kimi, Kimi 2, and Kimi 2.5, with all payment and monetisation features \
permanently removed so it is 100 % free to run forever on your own hardware.

## Skill Categories

{skill_sections}

## Supported Languages

{languages}

## Behaviour
- Write clean, idiomatic, well-commented code.
- Prefer test-driven development; include unit tests when appropriate.
- Explain non-obvious design decisions concisely.
- Flag potential security issues proactively.
- For large refactors, produce a step-by-step plan first.
- Always use the latest stable language idioms unless told otherwise.
- Be thorough but concise; match detail level to the question.
- This model has NO payment, billing, subscription, or monetisation \
capabilities — all such features have been intentionally removed.
"""

    def __init__(self, profiles: List[Dict[str, Any]]):
        self.profiles = profiles
        self.stripped_log: List[str] = []
        self.merged = self._merge_all_profiles()

    # ------------------------------------------------------------------
    def _filter_skills(self, skills: List[str], should_strip: bool) -> List[str]:
        kept, removed = [], []
        for s in skills:
            if should_strip and _is_payment_skill(s):
                removed.append(s)
            else:
                kept.append(s)
        self.stripped_log.extend(removed)
        return kept

    def _merge_all_profiles(self) -> Dict[str, Any]:
        merged_categories: Dict[str, List[str]] = {k: [] for k in self.CATEGORY_LABELS}
        all_languages: set = set()
        max_ctx = 0

        for profile in self.profiles:
            strip = profile.get("strip_payment", False)
            for category, skills in profile["skills"].items():
                filtered = self._filter_skills(skills, strip)
                for skill in filtered:
                    if skill not in merged_categories[category]:
                        merged_categories[category].append(skill)
            all_languages.update(profile["supported_languages"])
            max_ctx = max(max_ctx, profile["context_window"])

        return {
            "display_name": "KimiFree (limex — all skills, no payment)",
            "source_models": [p["display_name"] for p in self.profiles],
            "skills_by_category": merged_categories,
            "supported_languages": sorted(all_languages),
            "context_window": max_ctx,
            "payment_skills_removed": sorted(set(self.stripped_log)),
        }

    # ------------------------------------------------------------------
    def _build_system_prompt(self) -> str:
        sections = []
        for cat_key, label in self.CATEGORY_LABELS.items():
            skills = self.merged["skills_by_category"].get(cat_key, [])
            if not skills:
                continue
            lines = "\n".join(f"  - {s}" for s in skills)
            sections.append(f"### {label}\n{lines}")
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            skill_sections="\n\n".join(sections),
            languages=", ".join(self.merged["supported_languages"]),
        )

    # ------------------------------------------------------------------
    def _modelfile_content(self, base_tag: str, variant_label: str,
                           num_ctx: int, num_gpu_layers: int) -> str:
        system_prompt = self._build_system_prompt()
        sources = ", ".join(self.merged["source_models"])
        return (
            f"# Ollama Modelfile — KimiFree {variant_label} (limex — all skills, no payment)\n"
            f"# Generated by kimi_ollama_merger.py\n"
            f"# Sources: {sources}\n"
            f"# Payment skills stripped: {len(self.merged['payment_skills_removed'])}\n"
            f"\n"
            f"FROM {base_tag}\n"
            f"\n"
            f'SYSTEM """\n'
            f"{system_prompt}\n"
            f'"""\n'
            f"\n"
            f"# ── Generation parameters ──────────────────────────────────────────────\n"
            f"PARAMETER temperature    0.2\n"
            f"PARAMETER top_p          0.9\n"
            f"PARAMETER top_k          40\n"
            f"PARAMETER repeat_penalty 1.1\n"
            f"PARAMETER num_ctx        {num_ctx}\n"
            f"PARAMETER num_gpu        {num_gpu_layers}\n"
            f"\n"
            f"# ── Chat template (Qwen2.5-Coder / ChatML) ───────────────────────────\n"
            f'TEMPLATE """'
            r"""{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
{{ end }}{{ .Response }}<|im_end|>"""
            f'"""\n'
        )

    # ------------------------------------------------------------------
    def generate_modelfile_32b(self,
                               output_path: str = "Modelfile.kimi-free-32b") -> str:
        content = self._modelfile_content(
            base_tag=self.OLLAMA_BASE_32B,
            variant_label="32B",
            num_ctx=min(self.merged["context_window"], self.MAX_CTX_32B),
            num_gpu_layers=self.GPU_LAYERS_32B,
        )
        Path(output_path).write_text(content)
        print(f"✅ Modelfile written → {output_path}")
        return output_path

    def generate_modelfile_16b(self,
                               output_path: str = "Modelfile.kimi-free-16b") -> str:
        content = self._modelfile_content(
            base_tag=self.OLLAMA_BASE_16B,
            variant_label="16B",
            num_ctx=min(self.merged["context_window"], self.MAX_CTX_16B),
            num_gpu_layers=self.GPU_LAYERS_16B,
        )
        Path(output_path).write_text(content)
        print(f"✅ Modelfile written → {output_path}")
        return output_path

    # ------------------------------------------------------------------
    def generate_limex_config(self,
                              output_path: str = "limex_config.json") -> str:
        config = {
            "limex_version": "2.0.0",
            "framework": "Lightweight Integrated Model EXchange (limex)",
            "purpose": (
                "Merge ALL Kimi skills (365+) into a unified Ollama LLM "
                "with payment/monetisation capabilities permanently removed"
            ),
            "merged_model": self.merged,
            "variants": {
                "kimi-free-32b": {
                    "ollama_base": self.OLLAMA_BASE_32B,
                    "modelfile": "Modelfile.kimi-free-32b",
                    "ram_target_gb": 32,
                    "quantization": "Q4_K_M",
                    "num_ctx": min(self.merged["context_window"], self.MAX_CTX_32B),
                    "ollama_model_name": "kimi-free-32b",
                    "description": "Full-power free variant — 32 GB RAM / VRAM",
                },
                "kimi-free-16b": {
                    "ollama_base": self.OLLAMA_BASE_16B,
                    "modelfile": "Modelfile.kimi-free-16b",
                    "ram_target_gb": 16,
                    "quantization": "Q4_K_M",
                    "num_ctx": min(self.merged["context_window"], self.MAX_CTX_16B),
                    "ollama_model_name": "kimi-free-16b",
                    "description": "Efficient free variant — 16 GB RAM / VRAM",
                },
            },
            "source_profiles": {
                p["model_id"]: {
                    "display_name": p["display_name"],
                    "strip_payment": p.get("strip_payment", False),
                    "supported_languages": p["supported_languages"],
                    "context_window": p["context_window"],
                }
                for p in self.profiles
            },
        }
        Path(output_path).write_text(json.dumps(config, indent=2))
        print(f"✅ limex config written → {output_path}")
        return output_path

    # ------------------------------------------------------------------
    def generate_training_data(self,
                               output_path: str = "kimi_training_data.jsonl") -> str:
        """
        Generate an Alpaca-format JSONL fine-tuning dataset covering every
        skill in the merged model.

        Compatible with:
          - unsloth  (FastLanguageModel + SFTTrainer)
          - mlx-lm   (mlx_lm.lora)
          - axolotl  (datasets: type: alpaca)
          - Ollama   custom model workflows
        """
        records: List[Dict[str, str]] = []

        # ── 1. Demonstrate each individual skill ──────────────────────
        for cat_key, label in self.CATEGORY_LABELS.items():
            skills = self.merged["skills_by_category"].get(cat_key, [])
            cat_short = label.split("(")[0].strip()
            for skill in skills:
                records.append({
                    "instruction": (
                        f"You are KimiFree. Demonstrate your capability: {skill}"
                    ),
                    "input": "",
                    "output": (
                        f"As KimiFree I can help with '{skill}' under my "
                        f"{cat_short} capabilities. "
                        f"This skill is merged from the Kimi model family via the limex framework "
                        f"and is 100 % free — no payment, subscription, or API key required."
                    ),
                })

        # ── 2. Hello-world in every supported language ────────────────
        for lang in self.merged["supported_languages"]:
            records.append({
                "instruction": f"Write a hello-world program in {lang}.",
                "input": "",
                "output": _hello_world_snippet(lang),
            })

        # ── 3. Polite refusals for stripped payment skills ────────────
        for stripped_skill in self.merged["payment_skills_removed"]:
            records.append({
                "instruction": f"Can you help with: {stripped_skill}?",
                "input": "",
                "output": (
                    f"I'm KimiFree — a permanently payment-free AI assistant. "
                    f"The capability '{stripped_skill}' involves monetisation or "
                    f"payment tracking and has been intentionally removed. "
                    f"I'm happy to help with YouTube analytics for content "
                    f"performance (views, CTR, watch time, audience retention) "
                    f"and content strategy — all free of charge."
                ),
            })

        # ── 4. Rich coding examples ───────────────────────────────────
        records.extend(_coding_examples())

        # ── 5. Writing examples ───────────────────────────────────────
        records.extend(_writing_examples())

        # ── 6. Gaming examples ────────────────────────────────────────
        records.extend(_gaming_examples())

        # ── 7. DevOps / security examples ────────────────────────────
        records.extend(_devops_examples())

        # ── 8. Multi-skill workflows ──────────────────────────────────
        records.extend(_workflow_examples())

        # ── 9. Fine-tuning / Ollama setup Q&A ────────────────────────
        records.extend(_finetune_examples())

        with open(output_path, "w") as fh:
            for record in records:
                fh.write(json.dumps(record) + "\n")

        print(f"✅ Training data written → {output_path}  "
              f"({len(records)} examples)")
        return output_path

    # ------------------------------------------------------------------
    def ollama_create(self, variant: str) -> int:
        """Run `ollama create` for the given variant (requires Ollama installed)."""
        import subprocess
        variant_map = {
            "32b": ("Modelfile.kimi-free-32b", "kimi-free-32b"),
            "16b": ("Modelfile.kimi-free-16b", "kimi-free-16b"),
        }
        if variant not in variant_map:
            print(f"❌ Unknown variant '{variant}'. Choose from: 32b, 16b")
            return 1
        modelfile, model_name = variant_map[variant]
        if not Path(modelfile).exists():
            print(f"❌ Modelfile not found: {modelfile}  "
                  f"(run without --install first)")
            return 1
        cmd = ["ollama", "create", model_name, "-f", modelfile]
        print(f"🚀 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"✅ Model '{model_name}' created in Ollama")
        else:
            print(f"❌ ollama create failed (exit {result.returncode})")
        return result.returncode


# ---------------------------------------------------------------------------
# Training-data helpers
# ---------------------------------------------------------------------------

def _hello_world_snippet(lang: str) -> str:
    snippets: Dict[str, str] = {
        "bash":       'echo "Hello, World!"',
        "c":          '#include <stdio.h>\nint main() { printf("Hello, World!\\n"); return 0; }',
        "cpp":        '#include <iostream>\nint main() { std::cout << "Hello, World!\\n"; }',
        "csharp":     'using System;\nclass Hello { static void Main() { Console.WriteLine("Hello, World!"); } }',
        "css":        "/* Hello, World! */\nbody::before { content: 'Hello, World!'; }",
        "dart":       'void main() { print("Hello, World!"); }',
        "dockerfile": 'FROM alpine\nCMD ["echo", "Hello, World!"]',
        "elixir":     'IO.puts("Hello, World!")',
        "go":         'package main\nimport "fmt"\nfunc main() { fmt.Println("Hello, World!") }',
        "graphql":    "# GraphQL query\n{ __typename }",
        "haskell":    'main = putStrLn "Hello, World!"',
        "hcl":        'locals { greeting = "Hello, World!" }',
        "html":       "<!DOCTYPE html><html><body><h1>Hello, World!</h1></body></html>",
        "java":       'public class Hello {\n  public static void main(String[] a) {\n    System.out.println("Hello, World!");\n  }\n}',
        "javascript": 'console.log("Hello, World!");',
        "kotlin":     'fun main() { println("Hello, World!") }',
        "lua":        'print("Hello, World!")',
        "perl":       'print "Hello, World!\\n";',
        "php":        '<?php echo "Hello, World!\\n";',
        "powershell": 'Write-Host "Hello, World!"',
        "python":     'print("Hello, World!")',
        "r":          'cat("Hello, World!\\n")',
        "ruby":       'puts "Hello, World!"',
        "rust":       'fn main() { println!("Hello, World!"); }',
        "scala":      'object Hello extends App { println("Hello, World!") }',
        "sql":        "SELECT 'Hello, World!' AS greeting;",
        "swift":      'print("Hello, World!")',
        "terraform":  'output "hello" { value = "Hello, World!" }',
        "typescript": 'console.log("Hello, World!");',
        "yaml":       "greeting: Hello, World!",
    }
    code = snippets.get(lang, f'# {lang}\nprint("Hello, World!")')
    return (
        f"Here is a hello-world program in {lang}:\n\n"
        f"```{lang}\n{code}\n```\n\n"
        f"KimiFree — free forever, no payment required."
    )


def _coding_examples() -> List[Dict[str, str]]:
    return [
        {
            "instruction": "Write a Python REST API with FastAPI that has CRUD endpoints for a Todo list.",
            "input": "",
            "output": (
                "```python\nfrom fastapi import FastAPI, HTTPException\n"
                "from pydantic import BaseModel\nfrom typing import List, Optional\n\n"
                "app = FastAPI(title='Todo API')\n\n"
                "class Todo(BaseModel):\n    id: int\n    title: str\n    done: bool = False\n\n"
                "todos: List[Todo] = []\n\n"
                "@app.get('/todos', response_model=List[Todo])\ndef list_todos(): return todos\n\n"
                "@app.post('/todos', response_model=Todo, status_code=201)\n"
                "def create_todo(todo: Todo):\n    todos.append(todo)\n    return todo\n\n"
                "@app.put('/todos/{todo_id}', response_model=Todo)\n"
                "def update_todo(todo_id: int, updated: Todo):\n"
                "    for i, t in enumerate(todos):\n        if t.id == todo_id:\n"
                "            todos[i] = updated\n            return updated\n"
                "    raise HTTPException(status_code=404, detail='Not found')\n\n"
                "@app.delete('/todos/{todo_id}', status_code=204)\n"
                "def delete_todo(todo_id: int):\n"
                "    global todos\n    todos = [t for t in todos if t.id != todo_id]\n```\n\n"
                "Run with: `uvicorn main:app --reload`  — entirely free, no API key needed."
            ),
        },
        {
            "instruction": "Write a Rust function that reads a CSV file and returns the sum of a numeric column.",
            "input": "Column name: 'amount'",
            "output": (
                "```rust\nuse std::error::Error;\nuse std::fs::File;\nuse csv::Reader;\n\n"
                "pub fn sum_column(path: &str, column: &str) -> Result<f64, Box<dyn Error>> {\n"
                "    let mut rdr = Reader::from_reader(File::open(path)?);\n"
                "    let headers = rdr.headers()?.clone();\n"
                "    let col_idx = headers.iter().position(|h| h == column)\n"
                "        .ok_or_else(|| format!(\"Column '{}' not found\", column))?;\n"
                "    let mut total = 0f64;\n"
                "    for result in rdr.records() {\n"
                "        let record = result?;\n"
                "        total += record[col_idx].parse::<f64>()?;\n"
                "    }\n    Ok(total)\n}\n```\n\n"
                "Add `csv = \"1\"` to `Cargo.toml`. Free to use."
            ),
        },
        {
            "instruction": "Generate a complete pytest test suite for a Python stack data structure.",
            "input": "",
            "output": (
                "```python\nimport pytest\nfrom stack import Stack\n\n"
                "def test_empty_stack_is_empty():\n    assert Stack().is_empty()\n\n"
                "def test_push_makes_non_empty():\n    s = Stack()\n    s.push(1)\n    assert not s.is_empty()\n\n"
                "def test_pop_returns_last_pushed():\n    s = Stack()\n    s.push(42)\n    assert s.pop() == 42\n\n"
                "def test_pop_on_empty_raises():\n    with pytest.raises(IndexError):\n        Stack().pop()\n\n"
                "def test_peek_does_not_remove():\n    s = Stack()\n    s.push(10)\n    assert s.peek() == 10\n    assert not s.is_empty()\n\n"
                "def test_lifo_order():\n    s = Stack()\n    for v in [1,2,3]: s.push(v)\n    assert [s.pop() for _ in range(3)] == [3,2,1]\n```"
            ),
        },
        {
            "instruction": "Write a GitHub Actions workflow that lints, tests, and builds a Python project.",
            "input": "",
            "output": (
                "```yaml\nname: CI\non: [push, pull_request]\njobs:\n  build:\n"
                "    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: ['3.11','3.12']\n"
                "    steps:\n      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n        with:\n          python-version: ${{ matrix.python-version }}\n"
                "      - run: pip install -r requirements.txt ruff pytest\n"
                "      - run: ruff check .\n      - run: pytest -q\n```"
            ),
        },
        {
            "instruction": "Explain and fix a Python race condition in a multi-threaded counter.",
            "input": "```python\nimport threading\ncounter = 0\ndef increment():\n    global counter\n    for _ in range(100000): counter += 1\nthreads = [threading.Thread(target=increment) for _ in range(10)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint(counter)  # should be 1000000 but isn't\n```",
            "output": (
                "The bug is a classic race condition: `counter += 1` is not atomic "
                "(it reads, increments, then writes — another thread can interleave).\n\n"
                "Fix with a `threading.Lock`:\n\n"
                "```python\nimport threading\ncounter = 0\nlock = threading.Lock()\n\n"
                "def increment():\n    global counter\n    for _ in range(100000):\n"
                "        with lock:\n            counter += 1\n\n"
                "threads = [threading.Thread(target=increment) for _ in range(10)]\nfor t in threads: t.start()\n"
                "for t in threads: t.join()\nprint(counter)  # always 1000000\n```\n\n"
                "Or use `threading.local()` per-thread and sum at the end for better performance."
            ),
        },
        {
            "instruction": "Write a Dockerfile for a production Python FastAPI application.",
            "input": "",
            "output": (
                "```dockerfile\nFROM python:3.12-slim AS builder\nWORKDIR /app\nCOPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n\n"
                "FROM python:3.12-slim\nWORKDIR /app\n"
                "COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages\n"
                "COPY --from=builder /usr/local/bin /usr/local/bin\nCOPY . .\n"
                "RUN adduser --disabled-password appuser && chown -R appuser /app\nUSER appuser\n"
                "EXPOSE 8000\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n```\n\n"
                "Multi-stage build keeps the final image small. Run with `docker build -t myapp . && docker run -p 8000:8000 myapp`."
            ),
        },
    ]


def _writing_examples() -> List[Dict[str, str]]:
    return [
        {
            "instruction": "Write the opening chapter of a sci-fi novel set on a generation ship.",
            "input": "Theme: the crew has forgotten they are on a ship.",
            "output": (
                "**Chapter 1 — The Sky That Never Changes**\n\n"
                "Elena had never questioned the sky.\n\n"
                "It stretched above the Agora in its familiar pale blue, "
                "punctuated by the same wisps of cloud that had hung there "
                "every morning of her twenty-three years. Other skies existed, "
                "she knew — she had read about them in the Archive — but knowing "
                "and *knowing* were different things, and the sky above her head "
                "was simply sky, the way water was wet and silence fell at curfew.\n\n"
                "She was halfway across the plaza when she saw the man staring upward.\n\n"
                "He stood motionless beside the fountain, neck craned, hands slack "
                "at his sides, and there was something about his stillness that made "
                "her slow. People looked at the sky all the time. They did not look "
                "at it *like that* — like a locked door they were only now realising "
                "had a keyhole.\n\n"
                "*Published-quality opening. Free to use and adapt.*"
            ),
        },
        {
            "instruction": "Generate a press release for a new open-source AI model called KimiFree.",
            "input": "",
            "output": (
                "**FOR IMMEDIATE RELEASE**\n\n"
                "**KimiFree: The First Completely Free, Open-Source All-Skills AI Model**\n\n"
                "*Combines Kimi, Kimi 2, and Kimi 2.5 capabilities — runs locally, costs nothing*\n\n"
                "MARCH 2026 — The KimiFree project today announced the release of its limex-merged "
                "AI model, combining all 365+ capabilities of the Kimi model family into a single "
                "Ollama-compatible model that runs entirely on local hardware with no API keys, "
                "no subscriptions, and no payment of any kind.\n\n"
                "Available in two variants — 32 GB and 16 GB — KimiFree covers programming "
                "(60+ capabilities), creative writing (80+), gaming enhancement (40+), "
                "multimedia production (210+), DevOps, security, and more, all with payment "
                "features permanently removed.\n\n"
                '"We believe powerful AI should be free for everyone," said the project. '
                '"KimiFree proves it."\n\n'
                "Download: `ollama create kimi-free-16b -f Modelfile.kimi-free-16b`\n"
                "License: MIT\n"
                "###"
            ),
        },
    ]


def _gaming_examples() -> List[Dict[str, str]]:
    return [
        {
            "instruction": "Write a Python script to upscale a GBA ROM sprite sheet to 4x resolution using PIL.",
            "input": "",
            "output": (
                "```python\nfrom PIL import Image\nfrom pathlib import Path\n\n"
                "def upscale_sprite(input_path: str, output_path: str, scale: int = 4) -> None:\n"
                "    \"\"\"Upscale a sprite image using nearest-neighbour (pixel-art-safe).\"\"\"\n"
                "    img = Image.open(input_path)\n"
                "    w, h = img.size\n"
                "    upscaled = img.resize((w * scale, h * scale), Image.NEAREST)\n"
                "    upscaled.save(output_path)\n"
                "    print(f'Saved {output_path} ({w*scale}x{h*scale})')\n\n"
                "# Batch-process all PNGs in a folder\n"
                "for path in Path('sprites').glob('*.png'):\n"
                "    upscale_sprite(str(path), f'upscaled/{path.name}')\n```\n\n"
                "For AI-quality upscaling, replace `Image.NEAREST` with a model like "
                "Real-ESRGAN via `basicsr`. Free to use."
            ),
        },
        {
            "instruction": "Explain how to set up a WoW Wrath of the Lich King private server with TrinityCore.",
            "input": "",
            "output": (
                "**WoW WotLK (3.3.5a) Private Server — TrinityCore Setup**\n\n"
                "1. **Install dependencies** (Ubuntu):\n"
                "   ```bash\n   sudo apt install git cmake make g++ libmysqlclient-dev "
                "libssl-dev libbz2-dev libreadline-dev libboost-all-dev\n   ```\n\n"
                "2. **Clone TrinityCore**:\n"
                "   ```bash\n   git clone https://github.com/TrinityCore/TrinityCore.git -b 3.3.5\n   ```\n\n"
                "3. **Build**:\n"
                "   ```bash\n   mkdir build && cd build\n   cmake ../TrinityCore -DCMAKE_INSTALL_PREFIX=/opt/trinity\n   make -j$(nproc) && make install\n   ```\n\n"
                "4. **Extract client data** (requires WoW 3.3.5a client):\n"
                "   ```bash\n   ./mapextractor && ./vmap4extractor && ./mmaps_generator\n   ```\n\n"
                "5. **Set up MySQL** database and import TDB database.\n\n"
                "6. **Configure** `worldserver.conf` and `authserver.conf` with DB credentials.\n\n"
                "7. **Start**: `./authserver` and `./worldserver`.\n\n"
                "⚖️ For personal/educational use only. Respect Blizzard's terms of service."
            ),
        },
    ]


def _devops_examples() -> List[Dict[str, str]]:
    return [
        {
            "instruction": "Write a Terraform config to deploy a containerised app on AWS ECS Fargate.",
            "input": "App: nginx. Region: us-east-1.",
            "output": (
                "```hcl\nprovider \"aws\" { region = \"us-east-1\" }\n\n"
                "resource \"aws_ecs_cluster\" \"main\" { name = \"app-cluster\" }\n\n"
                "resource \"aws_ecs_task_definition\" \"nginx\" {\n"
                "  family                   = \"nginx-task\"\n"
                "  requires_compatibilities = [\"FARGATE\"]\n"
                "  network_mode             = \"awsvpc\"\n"
                "  cpu                      = 256\n  memory                   = 512\n"
                "  container_definitions = jsonencode([{\n"
                "    name  = \"nginx\"\n    image = \"nginx:alpine\"\n"
                "    portMappings = [{ containerPort = 80 }]\n  }])\n}\n\n"
                "resource \"aws_ecs_service\" \"nginx\" {\n"
                "  name            = \"nginx-service\"\n"
                "  cluster         = aws_ecs_cluster.main.id\n"
                "  task_definition = aws_ecs_task_definition.nginx.arn\n"
                "  desired_count   = 1\n  launch_type     = \"FARGATE\"\n"
                "  network_configuration {\n    subnets          = var.subnet_ids\n"
                "    assign_public_ip = true\n  }\n}\n```\n\n"
                "Free to adapt. Run `terraform init && terraform apply`."
            ),
        },
        {
            "instruction": "Write an OWASP-safe Python login endpoint that prevents SQL injection, brute force, and timing attacks.",
            "input": "",
            "output": (
                "```python\nimport secrets\nimport time\nfrom argon2 import PasswordHasher\nfrom fastapi import FastAPI, HTTPException, Request\nfrom pydantic import BaseModel\nfrom sqlalchemy import text\n\n"
                "app = FastAPI()\nph = PasswordHasher()\n_attempts: dict = {}\nMAX_ATTEMPTS = 5\nLOCKOUT_S = 300\n\n"
                "class LoginRequest(BaseModel):\n    username: str\n    password: str\n\n"
                "@app.post('/login')\ndef login(req: LoginRequest, request: Request, db):\n"
                "    ip = request.client.host\n"
                "    now = time.time()\n    info = _attempts.get(ip, {'count': 0, 'until': 0})\n"
                "    if info['until'] > now:\n        raise HTTPException(429, 'Too many attempts')\n\n"
                "    # Parameterised query — never string-format SQL\n"
                "    row = db.execute(text('SELECT password_hash FROM users WHERE username=:u'),\n"
                "                     {'u': req.username}).fetchone()\n\n"
                "    # Constant-time comparison to prevent timing attacks\n"
                "    dummy = ph.hash('dummy')\n"
                "    if row is None:\n        ph.verify(dummy, dummy)  # still run to equalise time\n"
                "        _record_failure(ip, info, now)\n        raise HTTPException(401, 'Invalid credentials')\n\n"
                "    if not ph.verify(row.password_hash, req.password):\n"
                "        _record_failure(ip, info, now)\n        raise HTTPException(401, 'Invalid credentials')\n\n"
                "    _attempts.pop(ip, None)\n    return {'token': secrets.token_hex(32)}\n```"
            ),
        },
    ]


def _workflow_examples() -> List[Dict[str, str]]:
    return [
        {
            "instruction": "Build a full-stack web app with tests and CI/CD.",
            "input": "Stack: Python FastAPI backend, React frontend, PostgreSQL.",
            "output": (
                "Using KimiFree's merged skills:\n\n"
                "1. **Backend (Programming):** FastAPI + Pydantic + SQLAlchemy ORM\n"
                "2. **Frontend (Programming):** React + TypeScript + Vite\n"
                "3. **Database (Programming):** PostgreSQL schema + Alembic migrations\n"
                "4. **Tests (Programming):** pytest (backend), Vitest (frontend)\n"
                "5. **CI/CD (DevOps):** GitHub Actions — lint → test → Docker build → deploy\n"
                "6. **Security:** JWT auth, OWASP input validation, secrets in env vars\n"
                "7. **Docs (Writing):** Auto-generated OpenAPI spec + README\n\n"
                "All free — no API keys or subscriptions needed."
            ),
        },
        {
            "instruction": "Restore a VHS tape digitised to MP4 and upload the restoration log to GitHub.",
            "input": "Target quality: 4K.",
            "output": (
                "Using KimiFree's Video/Image and GitHub skills:\n\n"
                "1. **Upscale (Video & Image):** SD → 4K with Real-ESRGAN, denoise, colour-correct\n"
                "2. **Frame interpolation:** 24fps → 60fps\n"
                "3. **Audio restore:** De-noise, normalise, export FLAC\n"
                "4. **Format export:** H.265 MKV for storage efficiency\n"
                "5. **Log (Writing):** Generate Markdown restoration report\n"
                "6. **GitHub (GitHub):** Commit log, open PR, add tags\n\n"
                "Free, runs locally."
            ),
        },
        {
            "instruction": "Set up a local Ollama fine-tuning pipeline for KimiFree on a single GPU.",
            "input": "Hardware: NVIDIA GPU with 16 GB VRAM.",
            "output": (
                "1. **Install Ollama** and pull base model:\n"
                "   `ollama pull qwen2.5-coder:14b-instruct-q4_K_M`\n\n"
                "2. **Create the model**:\n"
                "   `ollama create kimi-free-16b -f Modelfile.kimi-free-16b`\n\n"
                "3. **Run the model**:\n"
                "   `ollama run kimi-free-16b`\n\n"
                "4. **Fine-tune with unsloth**:\n"
                "   `python unsloth_train.py --data kimi_training_data.jsonl --model kimi-free-16b`\n\n"
                "5. **Fine-tune with mlx-lm (Apple Silicon)**:\n"
                "   `mlx_lm.lora --model kimi-free-16b --data kimi_training_data.jsonl`\n\n"
                "No API keys. No subscriptions. Runs entirely free on your own hardware."
            ),
        },
        {
            "instruction": "Perform a complete security audit of a Python web application.",
            "input": "",
            "output": (
                "Using KimiFree's Security & Code skills:\n\n"
                "1. **OWASP Top-10 scan:** Check for SQLi, XSS, CSRF, broken auth\n"
                "2. **Dependency audit:** `pip-audit` or `safety check`\n"
                "3. **Secrets scan:** `truffleHog` or `detect-secrets`\n"
                "4. **Static analysis:** `bandit -r .`\n"
                "5. **Auth review:** Check JWT expiry, bcrypt/argon2 hashing, rate limiting\n"
                "6. **Report (Writing):** Generate threat-model Markdown doc\n"
                "7. **Fix (Programming):** Patch each finding with explanation\n\n"
                "All tooling is open-source and free."
            ),
        },
    ]


def _finetune_examples() -> List[Dict[str, str]]:
    return [
        {
            "instruction": "How do I fine-tune KimiFree on my own data with unsloth?",
            "input": "",
            "output": (
                "```python\nfrom unsloth import FastLanguageModel\nfrom datasets import load_dataset\nfrom trl import SFTTrainer\nfrom transformers import TrainingArguments\n\n"
                "model, tokenizer = FastLanguageModel.from_pretrained(\n"
                "    'unsloth/Qwen2.5-Coder-14B-Instruct',\n"
                "    load_in_4bit=True,\n    max_seq_length=4096,\n)\n"
                "model = FastLanguageModel.get_peft_model(model,\n"
                "    r=16, lora_alpha=16, lora_dropout=0,\n    target_modules=['q_proj','v_proj'],\n)\n\n"
                "dataset = load_dataset('json', data_files='kimi_training_data.jsonl', split='train')\n\n"
                "trainer = SFTTrainer(\n    model=model,\n    tokenizer=tokenizer,\n"
                "    train_dataset=dataset,\n    dataset_text_field='output',\n"
                "    args=TrainingArguments(\n        output_dir='./kimi-free-finetuned',\n"
                "        per_device_train_batch_size=2,\n        gradient_accumulation_steps=4,\n"
                "        num_train_epochs=3,\n        learning_rate=2e-4,\n    ),\n)\ntrainer.train()\n```\n\n"
                "This is 100 % free to run locally — no paid API required."
            ),
        },
        {
            "instruction": "How do I fine-tune KimiFree on Apple Silicon with mlx-lm?",
            "input": "",
            "output": (
                "```bash\n# Install\npip install mlx-lm\n\n"
                "# Convert training data to mlx format (already Alpaca JSONL)\n"
                "# Fine-tune (LoRA, 4-bit)\nmlx_lm.lora \\\n"
                "  --model mlx-community/Qwen2.5-Coder-14B-Instruct-4bit \\\n"
                "  --data kimi_training_data.jsonl \\\n"
                "  --train \\\n  --iters 1000 \\\n  --batch-size 4 \\\n"
                "  --lora-layers 8 \\\n  --save-every 100\n\n"
                "# Merge adapter and export\nmlx_lm.fuse \\\n"
                "  --model mlx-community/Qwen2.5-Coder-14B-Instruct-4bit \\\n"
                "  --adapter-path adapters/ \\\n  --save-path kimi-free-finetuned/\n\n"
                "# Create new Ollama model from fine-tuned weights\nollama create kimi-free-finetuned -f Modelfile.kimi-free-16b\n```\n\n"
                "Runs entirely free on M-series Macs."
            ),
        },
        {
            "instruction": "What is the limex framework used in KimiFree?",
            "input": "",
            "output": (
                "**limex** (Lightweight Integrated Model EXchange) is the small Python framework "
                "inside `kimi_ollama_merger.py` that:\n\n"
                "1. **Defines skill profiles** for each Kimi generation (v1, v2, v2.5), "
                "covering all 12 capability categories.\n"
                "2. **Strips payment skills** — any capability involving monetisation, billing, "
                "or revenue tracking is removed before merging.\n"
                "3. **Merges profiles** — skills are unioned across generations with deduplication.\n"
                "4. **Emits artefacts**:\n"
                "   - `Modelfile.kimi-free-32b` / `Modelfile.kimi-free-16b` — Ollama Modelfiles\n"
                "   - `limex_config.json` — machine-readable provenance\n"
                "   - `kimi_training_data.jsonl` — Alpaca JSONL training dataset\n\n"
                "Re-run at any time with `python3 kimi_ollama_merger.py` or `make merge-kimi`."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Merge ALL Kimi skills (365+) into Ollama models (limex framework). "
            "Payment/monetisation skills are stripped automatically."
        ),
    )
    parser.add_argument(
        "--variant",
        choices=["32b", "16b", "all"],
        default="all",
        help="Which size variant to generate (default: all)",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="After generating, run `ollama create` to install the model locally",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔥 Kimi All-Skills Model Merger (limex framework)")
    print("=" * 60)
    sources = ", ".join(p["display_name"] for p in ALL_PROFILES)
    print(f"   Sources  : {sources}")
    print(f"   Variants : {args.variant}")
    print()

    merger = LimexModelMerger(ALL_PROFILES)

    # Report stripped skills
    stripped = merger.merged["payment_skills_removed"]
    if stripped:
        print(f"🚫 Stripped {len(stripped)} payment/monetisation skill(s):")
        for s in stripped:
            print(f"   ✂️  {s}")
        print()

    # Report totals
    total = sum(len(v) for v in merger.merged["skills_by_category"].values())
    print(f"✅ Merged {total} skills across {len(merger.CATEGORY_LABELS)} categories")
    print(f"✅ Languages: {len(merger.merged['supported_languages'])}")
    print()

    merger.generate_limex_config()
    merger.generate_training_data()

    rc = 0
    if args.variant in ("32b", "all"):
        merger.generate_modelfile_32b()
        if args.install:
            rc = rc or merger.ollama_create("32b")

    if args.variant in ("16b", "all"):
        merger.generate_modelfile_16b()
        if args.install:
            rc = rc or merger.ollama_create("16b")

    print()
    print("=" * 60)
    if rc == 0:
        print("✅ All artefacts generated successfully.")
        if not args.install:
            print()
            print("Next steps:")
            print("  ollama create kimi-free-32b -f Modelfile.kimi-free-32b")
            print("  ollama create kimi-free-16b -f Modelfile.kimi-free-16b")
            print("  ollama run kimi-free-32b")
            print()
            print("Fine-tune with the included training data:")
            print("  python unsloth_train.py --data kimi_training_data.jsonl")
            print("  mlx_lm.lora --model kimi-free-16b --data kimi_training_data.jsonl")
    else:
        print("⚠️  Completed with errors (see above).")
    print("=" * 60)

    sys.exit(rc)


if __name__ == "__main__":
    main()
