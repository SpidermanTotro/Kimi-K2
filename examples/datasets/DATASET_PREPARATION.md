# Dataset Preparation Guide for Kimi-K2 16-Layer Model

This guide provides instructions for preparing and organizing datasets for training the Kimi-K2 16-layer model across different domains.

## Overview

The Kimi-K2 16-layer model requires diverse, high-quality datasets to achieve proficiency in:
- Programming (multiple languages and frameworks)
- Writing and knowledge (creative, formal, encyclopedic)
- Animation and moviemaking (screenwriting, technical guidance)

## Dataset Structure

All datasets should follow this structure:

```
datasets/
├── programming/
│   ├── code_generation/
│   ├── code_understanding/
│   ├── debugging/
│   └── frameworks/
├── writing/
│   ├── creative/
│   ├── formal/
│   ├── knowledge/
│   └── summarization/
└── animation/
    ├── screenplays/
    ├── storyboards/
    └── technical/
```

## 1. Programming Datasets

### Required Datasets

#### The Stack (Code Generation)
```bash
# Download using Hugging Face datasets
from datasets import load_dataset

# Load specific programming languages
languages = ["python", "javascript", "java", "cpp", "go", "rust"]
for lang in languages:
    dataset = load_dataset(
        "bigcode/the-stack-dedup",
        data_dir=f"data/{lang}",
        split="train",
        streaming=True
    )
    # Process and save locally
```

#### CodeParrot (Python/JavaScript)
```bash
from datasets import load_dataset

dataset = load_dataset("codeparrot/codeparrot-clean", split="train")
# Filter for quality
filtered = dataset.filter(lambda x: len(x['content']) > 100 and len(x['content']) < 10000)
```

#### Code Contests (Algorithms & Problem Solving)
```bash
from datasets import load_dataset

dataset = load_dataset("deepmind/code_contests", split="train")
# Contains problems, solutions, and test cases
```

### Data Preprocessing for Programming

```python
def preprocess_code_dataset(example):
    """Preprocess code examples"""
    # Add language tags
    code = example['content']
    language = example.get('language', 'python')
    
    # Format with special tokens
    formatted = f"<|code_begin|><|lang:{language}|>\n{code}\n<|code_end|>"
    
    return {
        'text': formatted,
        'language': language,
        'metadata': {
            'length': len(code),
            'has_comments': '//' in code or '#' in code
        }
    }
```

### Quality Filters

Apply these filters to ensure high-quality code:
- Minimum length: 100 characters
- Maximum length: 10,000 characters
- Valid syntax (use language parsers)
- Contains meaningful variable names
- Has documentation or comments (optional but preferred)

## 2. Writing and Knowledge Datasets

### Required Datasets

#### Wikipedia (Encyclopedic Knowledge)
```bash
from datasets import load_dataset

# Load Wikipedia dataset
dataset = load_dataset("wikipedia", "20220301.en", split="train")

# Process articles
def process_wikipedia(example):
    return {
        'text': example['text'],
        'title': example['title'],
        'references': extract_references(example['text']),
    }
```

#### BookCorpus (Creative Writing)
```bash
from datasets import load_dataset

dataset = load_dataset("bookcorpus", split="train")
# Contains full books for narrative structure learning
```

#### ArXiv Papers (Scientific Writing)
```bash
# Download ArXiv dataset
wget https://www.kaggle.com/datasets/Cornell-University/arxiv

# Extract abstracts and full text
import json

def process_arxiv_paper(paper):
    return {
        'text': paper['abstract'] + '\n\n' + paper['body'],
        'title': paper['title'],
        'categories': paper['categories'],
        'citations': paper['references']
    }
```

### Data Preprocessing for Writing

```python
def preprocess_writing_dataset(example, style='academic'):
    """Preprocess writing examples"""
    text = example['text']
    
    # Add style markers
    formatted = f"<|style:{style}|>\n{text}"
    
    # Extract and mark citations
    citations = extract_citations(text)
    for i, citation in enumerate(citations):
        formatted = formatted.replace(
            citation, 
            f"<|ref:{i}|>{citation}<|/ref|>"
        )
    
    return {
        'text': formatted,
        'style': style,
        'word_count': len(text.split())
    }
```

### Quality Filters for Writing

- Minimum length: 500 words
- Proper grammar and spelling (use language tools)
- Coherent structure (paragraphs, sections)
- For academic: Must contain citations
- For creative: Proper narrative flow

## 3. Animation and Moviemaking Datasets

### Required Datasets

#### Movie Scripts
```bash
# Sources: IMSDB, Script Slug, etc.
# Manual collection or web scraping with permissions

def process_screenplay(script_text):
    """Process screenplay with proper formatting"""
    return {
        'text': script_text,
        'format': detect_format(script_text),  # Fountain, Final Draft, etc.
        'elements': extract_screenplay_elements(script_text),
        'genre': detect_genre(script_text)
    }
```

#### Cornell Movie Dialogs
```bash
from datasets import load_dataset

dataset = load_dataset("cornell_movie_dialogs", split="train")

def format_dialog(dialog):
    return {
        'text': f"<|dialogue_begin|>\n{dialog['text']}\n<|dialogue_end|>",
        'character': dialog['character'],
        'movie': dialog['movie']
    }
```

#### Web Animation Code (CSS/JS)
```bash
# Scrape from CodePen, JSFiddle (with API access)

def process_animation_code(code_example):
    return {
        'html': code_example['html'],
        'css': code_example['css'],
        'javascript': code_example['javascript'],
        'description': code_example['description'],
        'type': 'web_animation'
    }
```

### Screenplay Formatting

```python
def format_screenplay_element(element_type, content):
    """Format screenplay elements"""
    formats = {
        'scene_header': lambda x: f"<|scene_header|>{x.upper()}",
        'action': lambda x: f"<|action|>{x}",
        'character': lambda x: f"<|character|>{x.upper()}",
        'dialogue': lambda x: f"<|dialogue_begin|>{x}<|dialogue_end|>",
        'transition': lambda x: f"<|transition:{x.lower()}|>"
    }
    
    return formats.get(element_type, lambda x: x)(content)
```

## Dataset Mixing and Sampling

### Recommended Dataset Ratios

For balanced multi-domain training:

```yaml
dataset_mixing:
  programming: 0.40  # 40% of training data
  writing_knowledge: 0.35  # 35% of training data
  animation_moviemaking: 0.25  # 25% of training data

sampling_strategy: "temperature"  # or "proportional"
temperature: 0.8  # Controls diversity
```

### Implementing Dataset Mixing

```python
from datasets import interleave_datasets

# Load all datasets
prog_dataset = load_dataset("programming_combined")
writing_dataset = load_dataset("writing_combined")
animation_dataset = load_dataset("animation_combined")

# Mix with specified probabilities
mixed_dataset = interleave_datasets(
    [prog_dataset, writing_dataset, animation_dataset],
    probabilities=[0.40, 0.35, 0.25],
    seed=42
)
```

## Data Quality Assurance

### Automated Quality Checks

```python
def quality_check(example, domain):
    """Run quality checks on dataset examples"""
    checks = {
        'min_length': len(example['text']) >= 100,
        'max_length': len(example['text']) <= 50000,
        'valid_encoding': is_valid_utf8(example['text']),
        'no_excessive_repetition': not has_repetition(example['text']),
    }
    
    # Domain-specific checks
    if domain == 'programming':
        checks['valid_syntax'] = check_syntax(example['text'], example.get('language'))
    elif domain == 'writing':
        checks['proper_grammar'] = check_grammar(example['text'])
    
    return all(checks.values())
```

### Deduplication

```bash
# Use MinHash LSH for near-duplicate detection
from datasketch import MinHash, MinHashLSH

def deduplicate_dataset(dataset):
    lsh = MinHashLSH(threshold=0.85, num_perm=128)
    
    unique_items = []
    for item in dataset:
        m = MinHash(num_perm=128)
        for word in item['text'].split():
            m.update(word.encode('utf8'))
        
        # Check for duplicates
        result = lsh.query(m)
        if not result:
            lsh.insert(item['id'], m)
            unique_items.append(item)
    
    return unique_items
```

## Dataset Size Recommendations

For optimal training within memory constraints:

| Domain | Total Examples | Tokens (approx) | Disk Space |
|--------|---------------|-----------------|------------|
| Programming | 500,000 | 2B | ~15 GB |
| Writing & Knowledge | 400,000 | 3B | ~20 GB |
| Animation & Moviemaking | 200,000 | 1B | ~8 GB |
| **Total** | **1,100,000** | **6B** | **~43 GB** |

## Storage and Access

### Recommended Format

Use Hugging Face Datasets format for efficient loading:

```python
from datasets import Dataset, DatasetDict

# Save processed dataset
dataset.save_to_disk("./datasets/programming_processed")

# Load with memory mapping (efficient)
dataset = Dataset.load_from_disk(
    "./datasets/programming_processed",
    keep_in_memory=False  # Memory-efficient
)
```

### Streaming for Large Datasets

```python
from datasets import load_dataset

# Enable streaming to avoid loading entire dataset
dataset = load_dataset(
    "path/to/dataset",
    split="train",
    streaming=True  # Process on-the-fly
)

# Use with DataLoader
from torch.utils.data import DataLoader
dataloader = DataLoader(dataset, batch_size=8)
```

## Next Steps

1. Download and prepare datasets following this guide
2. Run quality checks and deduplication
3. Mix datasets according to recommended ratios
4. Verify total dataset size fits available storage
5. Test data loading pipeline with small sample
6. Begin training with appropriate configuration

For training configuration, see:
- `configs/training/programming_skills.yaml`
- `configs/training/writing_and_knowledge.yaml`
- `configs/training/animation_and_moviemaking.yaml`
