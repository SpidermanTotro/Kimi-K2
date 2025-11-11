# Training Data Enhancement - Phase 3

This directory contains utilities and scripts for preparing training data and fine-tuning Kimi K2.

## Overview

Phase 3 focuses on:
- Formatting 408K+ lines of code for instruction tuning
- Creating scaffolding for fine-tuning scripts
- Implementing data validation and quality checks

## Directory Structure

```
data/
├── formatters/         # Data formatting utilities
├── validators/         # Data validation scripts
├── processors/         # Data processing pipelines
├── datasets/           # Dataset configurations
└── README.md          # This file
```

## Data Formatting

### Supported Formats

1. **Instruction Tuning Format**
   - Input-output pairs
   - Multi-turn conversations
   - Task-specific formatting

2. **Code Data Format**
   - Function implementations
   - Code explanations
   - Bug fixes and patches

### Usage

```python
from forge.data.formatters import InstructionFormatter

# Format data for instruction tuning
formatter = InstructionFormatter()
formatted_data = formatter.format(raw_data)
```

## Data Processing Pipeline

1. **Collection**: Gather raw data from sources
2. **Cleaning**: Remove duplicates, filter quality
3. **Formatting**: Convert to training format
4. **Validation**: Check data integrity
5. **Export**: Save in training-ready format

## Data Validation

Ensure data quality with validation utilities:

```bash
python validate_data.py --input data.jsonl --output validated_data.jsonl
```

## Processing 408K+ Lines

The data processor handles large-scale datasets:

```bash
python process_large_dataset.py \
  --input raw_data/ \
  --output processed/ \
  --format instruction \
  --workers 8
```

## Quality Metrics

Track data quality with built-in metrics:
- Diversity score
- Length distribution
- Format compliance
- Content quality

## Next Steps

1. Integrate your data sources
2. Configure formatting parameters
3. Run processing pipeline
4. Validate output quality
5. Proceed to fine-tuning (see ../training/)
