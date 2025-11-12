# 🚀 Quick Start: Research Engine

## Get Information About Comet 3I/ATLAS in 3 Lines

```python
from forge_research_engine import ForgeResearchEngine

engine = ForgeResearchEngine()
comet = engine.get_astronomical_object("3I/2019 Q4")
print(f"{comet.name} - Discovered: {comet.discovery_date} by {comet.discoverer}")
```

**Output:**
```
Comet 2I/Borisov (3I/2019 Q4) - Discovered: 2019-08-30 by Gennadiy Borisov
```

---

## Search for Anything

```python
results = engine.search("your query here")
for result in results:
    print(f"{result.title} - Credibility: {result.source.credibility.name}")
```

---

## Fact-Check Any Claim

```python
fact = engine.fact_check("The Earth orbits the Sun")
print(f"Verified: {fact['verified']} - Confidence: {fact['confidence']:.0%}")
```

---

## Full Demo

Run the complete demonstration:

```bash
python3 demo_comet_research.py
```

This shows:
- Web search
- Astronomical object lookup
- Fact-checking
- Export functionality

---

## Documentation

- **Full Guide**: [docs/RESEARCH_CAPABILITIES.md](docs/RESEARCH_CAPABILITIES.md)
- **Implementation**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Main README**: [README.md](README.md)

---

## Features

✅ Multi-source web search  
✅ Astronomical object database  
✅ Fact-checking with confidence scores  
✅ Source credibility ratings (1-5)  
✅ Citation management  
✅ **NO FAKE NEWS** - Only verified sources  

---

## Verified Sources

- NASA JPL Small-Body Database (5/5)
- IAU Minor Planet Center (5/5)
- arXiv.org (5/5)
- Reuters (5/5)
- Associated Press (5/5)
- And more...

---

**Ready to explore? Start with `python3 demo_comet_research.py`** 🌟
