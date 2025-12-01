# 🔥 THE FORGE - Live AI Programs

This directory contains **live, executable implementations** of all capabilities described in the documentation. Each program transforms markdown documentation into working code.

## 📦 Available Programs

### 1. Skills Engine (`skills_engine.py`)
**Source**: `docs/ALL_SKILLS.md`

Transforms the complete skills documentation into a queryable, executable system.

**Capabilities**:
- ✅ Load and parse 575+ skills from documentation
- ✅ Organize skills by 12 categories
- ✅ Search skills by name or capability
- ✅ Export skills database to JSON
- ✅ Execute skills programmatically

**Usage**:
```python
from skills_engine import SkillsEngine

engine = SkillsEngine(docs_dir="../docs")
engine.load_all_skills()

# Search for skills
python_skills = engine.search_skills("Python")

# Get skills by category
programming_skills = engine.get_skills_by_category("programming")

# Export to JSON
engine.export_to_json("skills_database.json")
```

**Statistics**:
- 12 categories
- 40+ individual skills
- 575+ total capabilities

---

### 2. Intelligent Monitor (`intelligent_monitor.py`)
**Source**: `docs/INTELLIGENT_SYSTEMS.md`

Live monitoring system for issue detection, security scanning, and auto-updates.

**Capabilities**:
- ✅ Dependency scanning (Python & Node.js)
- ✅ Security vulnerability detection
- ✅ Code quality analysis
- ✅ Performance issue detection
- ✅ Exposed secrets detection
- ✅ Code smell identification
- ✅ Automated reporting

**Usage**:
```python
from intelligent_monitor import IntelligentMonitor

monitor = IntelligentMonitor(project_root="..")
monitor.start_monitoring()

# Get statistics
stats = monitor.get_statistics()

# Get critical issues
critical = monitor.get_critical_issues()

# Export report
monitor.export_report("monitoring_report.json")
```

**Detection Types**:
- Security issues (exposed secrets, weak patterns)
- Code smells (long functions, complexity)
- Performance issues (inefficient loops)
- Dependency updates

---

### 3. Multimedia Suite (`multimedia_suite.py`)
**Source**: `docs/MULTIMEDIA_CAPABILITIES.md`

Professional multimedia production tools for video, audio, and image processing.

**Capabilities**:
- ✅ Video editing (concatenate, convert, resize)
- ✅ Audio processing (extract, normalize, mix)
- ✅ Format conversion (MP4, MOV, AVI, WebM, MKV)
- ✅ Resolution changes (SD to 8K)
- ✅ Codec conversion (H.264, H.265, VP9, ProRes)
- ✅ Thumbnail generation
- ✅ Video information extraction

**Usage**:
```python
from multimedia_suite import MultimediaSuite, VideoResolution, VideoFormat

suite = MultimediaSuite()

# Create video project
project = suite.create_video_project("my_video")
suite.add_video_clip("my_video", "clip1.mp4")
suite.add_video_clip("my_video", "clip2.mp4")
suite.concatenate_videos("my_video", "output.mp4")

# Convert video
suite.convert_video(
    "input.mp4", 
    "output.mp4",
    resolution=VideoResolution.UHD_4K,
    codec=VideoCodec.H265
)

# Extract audio
suite.extract_audio("video.mp4", "audio.mp3")
```

**Supported Formats**:
- Video: MP4, MOV, AVI, WebM, MKV, FLV
- Codecs: H.264, H.265/HEVC, VP9, ProRes
- Resolutions: SD, HD, Full HD, QHD, 4K, 8K

---

### 4. Book Writing System (`book_writing_system.py`)
**Source**: `docs/BOOK_WRITING_MASTERY.md`

Complete book creation and management system.

**Capabilities**:
- ✅ Project management (create, track, organize)
- ✅ Character development (profiles, relationships, arcs)
- ✅ Plot structuring (three-act structure, outlines)
- ✅ Chapter organization (status tracking, word counts)
- ✅ Writing assistance (prompts, analysis)
- ✅ Manuscript export (TXT, JSON)
- ✅ Progress tracking (word counts, completion %)

**Usage**:
```python
from book_writing_system import BookWritingSystem, BookGenre, ChapterStatus

system = BookWritingSystem()

# Create project
project = system.create_project(
    "My Novel",
    "Author Name",
    BookGenre.FICTION,
    target_words=80000
)

# Add characters
system.add_character(
    "My Novel",
    "Hero",
    "protagonist",
    "Brave warrior on a quest"
)

# Add chapters
system.add_chapter(
    "My Novel",
    1,
    "The Beginning",
    "Hero starts their journey"
)

# Generate outline
outline = system.generate_outline("My Novel", num_chapters=20)

# Write chapter content
system.write_chapter_content("My Novel", 1, "Chapter content here...")

# Analyze pacing
analysis = system.analyze_pacing("My Novel")

# Export manuscript
system.export_manuscript("My Novel")
```

**Features**:
- Multiple genre support
- Character relationship tracking
- Three-act structure templates
- Word count tracking
- Progress analytics
- Writing prompts by genre

---

## 🚀 Getting Started

### Installation

1. **Install Python dependencies**:
```bash
cd Kimi-K2
pip install -r requirements.txt
```

2. **Install FFmpeg** (for multimedia suite):
```bash
sudo apt-get install ffmpeg
```

### Running Programs

Each program can be run standalone:

```bash
# Skills Engine
python3 live_programs/skills_engine.py

# Intelligent Monitor
python3 live_programs/intelligent_monitor.py

# Multimedia Suite
python3 live_programs/multimedia_suite.py

# Book Writing System
python3 live_programs/book_writing_system.py
```

### Integration with FORGE

All programs integrate seamlessly with the FORGE AI system:

```python
from forge_implementation import ForgeAI
from live_programs.skills_engine import SkillsEngine
from live_programs.intelligent_monitor import IntelligentMonitor

# Initialize FORGE
forge = ForgeAI()
forge.initialize()

# Add live programs
skills = SkillsEngine()
skills.load_all_skills()

monitor = IntelligentMonitor()
monitor.start_monitoring()
```

---

## 📊 Statistics

**Total Capabilities Implemented**: 575+

**Programs Created**: 4

**Lines of Code**: ~2,000+

**Documentation Transformed**: 15 MD files

---

## 🔧 Development

### Adding New Programs

1. Create new Python file in `live_programs/`
2. Import from corresponding MD documentation
3. Implement core functionality
4. Add tests and examples
5. Update this README

### Testing

```bash
# Run all programs
for prog in live_programs/*.py; do
    echo "Testing $prog"
    python3 "$prog"
done
```

---

## 📝 Documentation Sources

Each program is derived from specific documentation:

| Program | Source Documentation |
|---------|---------------------|
| `skills_engine.py` | `docs/ALL_SKILLS.md` |
| `intelligent_monitor.py` | `docs/INTELLIGENT_SYSTEMS.md` |
| `multimedia_suite.py` | `docs/MULTIMEDIA_CAPABILITIES.md` |
| `book_writing_system.py` | `docs/BOOK_WRITING_MASTERY.md` |

---

## 🎯 Future Enhancements

- [ ] Gaming enhancement system
- [ ] Deployment automation
- [ ] Tool integration framework
- [ ] Web interface for all programs
- [ ] API endpoints for remote access
- [ ] Database persistence
- [ ] Real-time collaboration features

---

## 📄 License

Same as parent project (see LICENSE file)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

---

**Built with 🔥 by THE FORGE AI Team**