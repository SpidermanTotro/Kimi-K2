# Training and Fine-Tuning Guide for Animation AI

## Overview

This guide explains how to train and fine-tune the Kimi-K2 Animation AI module on custom datasets for improved claymation and animation generation.

## Dataset Structure

### Claymation Datasets

#### Format

Claymation sequences should be stored as JSON files with the following structure:

```json
{
  "metadata": {
    "source": "wallace-gromit",
    "scene": "living_room",
    "fps": 24,
    "style": "aardman"
  },
  "sequence": {
    "name": "Wallace Grabs Cheese",
    "fps": 24,
    "keyframes": [
      {
        "id": 0,
        "timestamp": 0.0,
        "objects": [...]
      }
    ]
  }
}
```

#### Directory Structure

```
datasets/claymation/
├── aardman/
│   ├── wallace-gromit/
│   │   ├── sequence_001.json
│   │   ├── sequence_002.json
│   │   └── metadata.yaml
│   ├── chicken-run/
│   └── shaun-sheep/
├── robot-chicken/
│   ├── season_01/
│   └── season_02/
└── general/
    ├── classic/
    └── modern/
```

### Animation Datasets

#### Format

Animation loops stored as JSON:

```json
{
  "metadata": {
    "type": "walk_cycle",
    "character_type": "humanoid",
    "fps": 30,
    "duration": 1.0
  },
  "animation": {
    "name": "Natural Walk",
    "type": "3D",
    "loop_type": "walk",
    "keyframes": [...]
  }
}
```

## Training Data Collection

### 1. Claymation Data

#### Sources

1. **Public Domain Content**
   - Classic stop-motion films (pre-1928)
   - Creative Commons animations
   - Open-source projects

2. **Licensed Content**
   - Aardman style studies
   - Educational materials
   - Studio-provided references

3. **Generated Data**
   - Synthetic sequences from animation software
   - Procedurally generated motions
   - Physics simulations

#### Collection Method

```python
# Example: Extract frames from video
import cv2
import json

def extract_claymation_frames(video_path, output_dir):
    """Extract frames and metadata from claymation video."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    frames = []
    frame_id = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect objects and positions (simplified)
        objects = detect_objects(frame)
        
        frames.append({
            "id": frame_id,
            "timestamp": frame_id / fps,
            "objects": objects
        })
        
        frame_id += 1
    
    # Save sequence
    sequence = {
        "name": "Extracted Sequence",
        "fps": fps,
        "keyframes": frames[::4]  # Sample every 4th frame as keyframe
    }
    
    with open(f"{output_dir}/sequence.json", 'w') as f:
        json.dump(sequence, f, indent=2)
    
    cap.release()
```

### 2. Animation Loop Data

#### Generation Pipeline

```python
def generate_training_loops(count=1000):
    """Generate diverse animation loops for training."""
    import random
    
    loop_types = ["walk", "idle", "run", "jump"]
    variations = []
    
    for i in range(count):
        loop_type = random.choice(loop_types)
        
        # Vary parameters
        fps = random.choice([24, 30, 60])
        speed = random.uniform(0.8, 1.2)
        style = random.choice(["realistic", "cartoony", "robotic"])
        
        # Generate loop
        loop = generate_animation_loop(
            loop_type=loop_type,
            fps=fps,
            speed=speed,
            style=style
        )
        
        variations.append({
            "metadata": {
                "loop_type": loop_type,
                "fps": fps,
                "speed": speed,
                "style": style
            },
            "animation": loop
        })
    
    return variations
```

## Model Training

### Configuration

Update `animation/config/animation_config.yaml`:

```yaml
training:
  # Dataset paths
  datasets:
    claymation:
      - name: "Aardman Classics"
        path: "datasets/claymation/aardman"
        weight: 1.0
      - name: "Robot Chicken"
        path: "datasets/claymation/robot-chicken"
        weight: 0.8
      - name: "General Stop-Motion"
        path: "datasets/claymation/general"
        weight: 0.5
    
    animation:
      - name: "2D Loops"
        path: "datasets/animation/2d"
        weight: 0.7
      - name: "3D Loops"
        path: "datasets/animation/3d"
        weight: 1.0
  
  # Training parameters
  parameters:
    batch_size: 32
    learning_rate: 0.0001
    epochs: 100
    validation_split: 0.2
    
  # Model architecture
  model:
    embedding_dim: 512
    num_layers: 8
    num_heads: 8
    dropout: 0.1
```

### Training Script

Create `train_animation_model.py`:

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import json
import glob

class AnimationDataset(torch.utils.data.Dataset):
    def __init__(self, data_paths, transform=None):
        self.sequences = []
        
        for path in data_paths:
            files = glob.glob(f"{path}/**/*.json", recursive=True)
            for file in files:
                with open(file) as f:
                    self.sequences.append(json.load(f))
        
        self.transform = transform
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        
        # Convert sequence to tensor format
        # (This is simplified - real implementation needs proper encoding)
        frames = sequence.get('keyframes', [])
        
        # Extract features
        features = self.extract_features(frames)
        
        if self.transform:
            features = self.transform(features)
        
        return features
    
    def extract_features(self, frames):
        # Extract position, rotation, velocity, etc.
        # Return as tensor
        pass

class AnimationTransformer(nn.Module):
    def __init__(self, input_dim=512, num_heads=8, num_layers=6):
        super().__init__()
        
        self.embedding = nn.Linear(input_dim, 512)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=512,
            nhead=num_heads,
            dim_feedforward=2048,
            dropout=0.1
        )
        
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        self.output = nn.Linear(512, input_dim)
    
    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x)
        x = self.output(x)
        return x

def train_model(config_path="animation/config/animation_config.yaml"):
    # Load config
    with open(config_path) as f:
        import yaml
        config = yaml.safe_load(f)
    
    # Create datasets
    train_dataset = AnimationDataset(
        data_paths=config['training']['datasets']['animation']
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['parameters']['batch_size'],
        shuffle=True
    )
    
    # Initialize model
    model = AnimationTransformer(
        num_heads=config['training']['model']['num_heads'],
        num_layers=config['training']['model']['num_layers']
    )
    
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config['training']['parameters']['learning_rate']
    )
    
    criterion = nn.MSELoss()
    
    # Training loop
    for epoch in range(config['training']['parameters']['epochs']):
        model.train()
        total_loss = 0
        
        for batch in train_loader:
            optimizer.zero_grad()
            
            # Forward pass
            output = model(batch)
            loss = criterion(output, batch)  # Simplified
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{config['training']['parameters']['epochs']}, "
              f"Loss: {avg_loss:.4f}")
        
        # Save checkpoint
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
            }, f'checkpoint_epoch_{epoch + 1}.pth')
    
    # Save final model
    torch.save(model.state_dict(), 'animation_model_final.pth')
    print("Training complete!")

if __name__ == "__main__":
    train_model()
```

## Fine-Tuning Kimi-K2 for Animation

### 1. Prepare Fine-Tuning Dataset

```python
def create_finetuning_dataset():
    """Create dataset for fine-tuning Kimi-K2 on animation tasks."""
    
    examples = [
        # Animation generation examples
        {
            "messages": [
                {"role": "system", "content": "You are an expert animator."},
                {"role": "user", "content": "Create a walk cycle for a character"},
                {"role": "assistant", "content": "I'll generate a walk cycle animation.",
                 "tool_calls": [{
                     "function": {
                         "name": "generate_animation_loop",
                         "arguments": '{"loop_type": "walk", "animation_type": "3D"}'
                     }
                 }]}
            ]
        },
        
        # Quality analysis examples
        {
            "messages": [
                {"role": "user", "content": "How can I improve this claymation sequence?"},
                {"role": "assistant", "content": "Let me analyze the sequence quality first.",
                 "tool_calls": [{
                     "function": {
                         "name": "analyze_sequence_quality",
                         "arguments": '{"sequence_file": "input.json"}'
                     }
                 }]},
                {"role": "tool", "content": '{"quality_score": 45.5, "suggestions": [...]}'},
                {"role": "assistant", "content": "Based on the analysis (quality score: 45.5), "
                                                "I recommend adding more intermediate frames..."}
            ]
        },
        
        # Style selection examples
        {
            "messages": [
                {"role": "user", "content": "What animation style would work best for a children's show?"},
                {"role": "assistant", "content": "For a children's show, I'd recommend the Wallace and Gromit "
                                                "style. It's charming, smooth, and appealing to kids. "
                                                "Let me apply it to your sequence.",
                 "tool_calls": [{
                     "function": {
                         "name": "apply_style_preset",
                         "arguments": '{"style": "wallace-gromit"}'
                     }
                 }]}
            ]
        }
    ]
    
    # Save as JSONL for fine-tuning
    with open("animation_finetuning.jsonl", 'w') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')

create_finetuning_dataset()
```

### 2. Fine-Tune Using Kimi-K2

```python
# Example using the Kimi-K2 API for fine-tuning
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1")

# Upload training file
with open("animation_finetuning.jsonl", "rb") as f:
    response = client.files.create(
        file=f,
        purpose="fine-tune"
    )

file_id = response.id

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="kimi-k2-base",
    hyperparameters={
        "n_epochs": 3,
        "batch_size": 4,
        "learning_rate_multiplier": 0.1
    }
)

print(f"Fine-tuning job created: {job.id}")
```

## Style-Specific Training

### Wallace and Gromit Style

Training data should emphasize:
- Smooth, flowing movements
- Exaggerated but charming expressions
- Gentle easing on all transitions
- High-quality intermediate frames

### Robot Chicken Style

Training data should emphasize:
- Snappy, quick movements
- Comedy timing
- Abrupt but intentional transitions
- Fast-paced action

### Classic Stop-Motion

Training data should emphasize:
- Visible frame-by-frame progression
- Minimal smoothing
- Traditional animation principles
- Authentic stop-motion feel

## Evaluation Metrics

### Quality Metrics

1. **Smoothness Score**: Measure transition quality
2. **Temporal Consistency**: Check frame-to-frame coherence
3. **Style Adherence**: Compare to reference style
4. **User Preference**: A/B testing with animators

### Evaluation Script

```python
def evaluate_animation_quality(generated_seq, reference_seq):
    """Evaluate generated animation against reference."""
    
    metrics = {}
    
    # Smoothness
    metrics['smoothness'] = calculate_smoothness(generated_seq)
    
    # Temporal consistency
    metrics['consistency'] = calculate_consistency(generated_seq)
    
    # Style similarity
    metrics['style_match'] = compare_styles(generated_seq, reference_seq)
    
    # Overall quality
    metrics['overall'] = (
        metrics['smoothness'] * 0.4 +
        metrics['consistency'] * 0.3 +
        metrics['style_match'] * 0.3
    )
    
    return metrics
```

## Dataset Augmentation

Increase training data diversity:

```python
def augment_animation_data(sequence):
    """Augment animation sequence."""
    
    augmented = []
    
    # Speed variations
    for speed in [0.8, 1.0, 1.2]:
        augmented.append(adjust_speed(sequence, speed))
    
    # Mirror/flip
    augmented.append(mirror_sequence(sequence))
    
    # Noise injection
    augmented.append(add_noise(sequence, amount=0.05))
    
    # Scale variations
    for scale in [0.9, 1.0, 1.1]:
        augmented.append(scale_sequence(sequence, scale))
    
    return augmented
```

## Best Practices

1. **Dataset Quality > Quantity**
   - Curate high-quality examples
   - Remove broken or poor sequences
   - Verify all metadata

2. **Balanced Training**
   - Equal representation of all loop types
   - Diverse styles and character types
   - Various animation speeds

3. **Regular Validation**
   - Test on held-out data
   - Compare to baseline
   - Get feedback from animators

4. **Incremental Updates**
   - Start with small dataset
   - Gradually add more data
   - Re-train periodically

## Resources

- Dataset templates: `animation/config/animation_config.yaml`
- Training scripts: `scripts/training/`
- Evaluation tools: `scripts/evaluation/`

## Support

For training assistance:
- Check documentation in `docs/`
- Email: support@moonshot.cn
