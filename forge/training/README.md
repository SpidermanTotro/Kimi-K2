# Fine-Tuning Infrastructure - Phase 3

This directory contains fine-tuning scripts and configurations for Kimi K2.

## Overview

The fine-tuning infrastructure provides:
- Training script templates
- Configuration management
- Distributed training support
- Checkpoint management

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure training
cp configs/default.yaml configs/my_training.yaml
# Edit my_training.yaml with your settings

# Start fine-tuning
python scripts/finetune.py --config configs/my_training.yaml
```

## Configuration

Edit configuration files in `configs/` to customize:
- Model parameters
- Training hyperparameters
- Data paths
- Hardware settings

## Training Scripts

### Basic Fine-tuning

```bash
python scripts/finetune.py \
  --config configs/instruction_tuning.yaml \
  --data path/to/formatted_data.jsonl \
  --output models/kimi-k2-finetuned
```

### Distributed Training

```bash
torchrun --nproc_per_node=8 scripts/finetune_distributed.py \
  --config configs/distributed.yaml
```

## Monitoring

Track training progress:
- TensorBoard: `tensorboard --logdir logs/`
- Weights & Biases: Configure in training config
- Checkpoints saved in `checkpoints/`

## Best Practices

1. **Data Preparation**: Use validated data from `../data/`
2. **Checkpointing**: Save checkpoints every N steps
3. **Validation**: Monitor validation metrics
4. **Resources**: Match batch size to available GPU memory

## Supported Techniques

- Full fine-tuning
- LoRA (Low-Rank Adaptation)
- QLoRA (Quantized LoRA)
- Instruction tuning
- RLHF (Reinforcement Learning from Human Feedback)
