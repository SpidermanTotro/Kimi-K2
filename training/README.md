# Kimi K2 Training Enhancements

This directory contains training utilities and pipelines for Kimi K2 model enhancement.

## Features

- **Data Augmentation**: Generate synthetic training data
- **Multi-pass Fine-tuning**: Iterative refinement pipelines
- **Training Metrics**: Comprehensive tracking and visualization
- **Distributed Training**: Support for multi-GPU and multi-node training

## Directory Structure

```
training/
├── augmentation/    # Data augmentation tools
├── pipelines/       # Training pipelines
└── README.md        # This file
```

## Data Augmentation

### Supported Techniques

1. **Paraphrasing**: Generate paraphrased versions of training samples
2. **Back-translation**: Translate to another language and back
3. **Noise Injection**: Add controlled noise to improve robustness
4. **Adversarial Examples**: Generate challenging examples
5. **Template-based Generation**: Use templates to create variations

### Usage

```python
from training.augmentation.augmentor import DataAugmentor

# Initialize augmentor
augmentor = DataAugmentor()

# Augment data
original_data = [
    {"input": "What is AI?", "output": "AI stands for Artificial Intelligence..."}
]

augmented_data = augmentor.augment(
    data=original_data,
    techniques=['paraphrase', 'back_translate'],
    augmentation_factor=3
)
```

## Multi-pass Fine-tuning

### Pipeline Stages

1. **Initial Fine-tuning**: Base model adaptation
2. **Task-specific Training**: Focused on specific capabilities
3. **Refinement**: Polish and improve specific weaknesses
4. **Evaluation**: Comprehensive testing

### Example Pipeline

```python
from training.pipelines.multipass import MultiPassTrainer

trainer = MultiPassTrainer(
    base_model="Kimi-K2-Base",
    output_dir="./models/finetuned"
)

# Define training passes
passes = [
    {
        "name": "general",
        "data": "data/general_qa.jsonl",
        "epochs": 3,
        "learning_rate": 2e-5
    },
    {
        "name": "coding",
        "data": "data/coding_tasks.jsonl",
        "epochs": 2,
        "learning_rate": 1e-5
    },
    {
        "name": "refinement",
        "data": "data/refinement.jsonl",
        "epochs": 1,
        "learning_rate": 5e-6
    }
]

# Run multi-pass training
trainer.train(passes)
```

## Training Configuration

Configure training in `config.yaml`:

```yaml
training:
  batch_size: 8
  gradient_accumulation_steps: 4
  max_steps: 10000
  warmup_steps: 1000
  save_steps: 500
  eval_steps: 500
  
optimization:
  optimizer: adamw
  learning_rate: 2e-5
  weight_decay: 0.01
  max_grad_norm: 1.0
  
distributed:
  backend: nccl
  find_unused_parameters: false
```

## Monitoring

Training metrics are automatically exported to:
- TensorBoard
- Weights & Biases (optional)
- Custom logging files

## Best Practices

1. **Data Quality**: Use high-quality, diverse training data
2. **Validation**: Always validate on held-out data
3. **Checkpointing**: Save checkpoints regularly
4. **Monitoring**: Track metrics closely during training
5. **Ablation Studies**: Test different configurations

## Resources

- [Data Augmentation Guide](augmentation/README.md)
- [Pipeline Configuration](pipelines/README.md)
- [Training Best Practices](docs/BEST_PRACTICES.md)
