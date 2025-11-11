#!/usr/bin/env python3
"""
Fine-tuning Script for Kimi K2
THE FORGE AI - Phase 3: Training Data Enhancement

Scaffold for fine-tuning Kimi K2 on custom datasets.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional

import yaml
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    default_data_collator
)


class InstructionDataset(Dataset):
    """Dataset for instruction tuning."""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 8192):
        """Initialize dataset."""
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Load data
        with open(data_path, 'r') as f:
            self.data = [json.loads(line) for line in f]
        
        print(f"Loaded {len(self.data)} training examples")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        """Get a single training example."""
        item = self.data[idx]
        
        # Format messages using chat template
        text = self.tokenizer.apply_chat_template(
            item['messages'],
            tokenize=False,
            add_generation_prompt=False
        )
        
        # Tokenize
        encoded = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        # Create labels (same as input_ids for causal LM)
        encoded['labels'] = encoded['input_ids'].clone()
        
        return {
            'input_ids': encoded['input_ids'].squeeze(),
            'attention_mask': encoded['attention_mask'].squeeze(),
            'labels': encoded['labels'].squeeze()
        }


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def setup_model_and_tokenizer(config: Dict):
    """Setup model and tokenizer."""
    print(f"Loading model: {config['model']['name']}")
    
    tokenizer = AutoTokenizer.from_pretrained(
        config['model']['name'],
        trust_remote_code=config['model'].get('trust_remote_code', True)
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        config['model']['name'],
        trust_remote_code=config['model'].get('trust_remote_code', True),
        torch_dtype=torch.bfloat16 if config['training'].get('bf16') else torch.float32,
    )
    
    return model, tokenizer


def main():
    """Main fine-tuning entry point."""
    parser = argparse.ArgumentParser(description='Fine-tune Kimi K2')
    parser.add_argument('--config', required=True, help='Path to config file')
    parser.add_argument('--data', help='Override training data path')
    parser.add_argument('--output', help='Override output directory')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override paths if specified
    if args.data:
        config['data']['train_file'] = args.data
    if args.output:
        config['logging']['output_dir'] = args.output
    
    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(config)
    
    # Create datasets
    print("Loading datasets...")
    train_dataset = InstructionDataset(
        config['data']['train_file'],
        tokenizer,
        config['data']['max_length']
    )
    
    val_dataset = None
    if config['data'].get('val_file'):
        val_dataset = InstructionDataset(
            config['data']['val_file'],
            tokenizer,
            config['data']['max_length']
        )
    
    # Setup training arguments
    training_args = TrainingArguments(
        output_dir=config['logging']['output_dir'],
        num_train_epochs=config['training']['num_epochs'],
        per_device_train_batch_size=config['data']['batch_size'],
        gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],
        learning_rate=config['training']['learning_rate'],
        weight_decay=config['training']['weight_decay'],
        warmup_steps=config['training']['warmup_steps'],
        max_grad_norm=config['training']['max_grad_norm'],
        fp16=config['training'].get('fp16', False),
        bf16=config['training'].get('bf16', False),
        logging_steps=config['logging']['log_interval'],
        save_steps=config['logging']['save_interval'],
        eval_steps=config['logging']['eval_interval'],
        evaluation_strategy="steps" if val_dataset else "no",
        save_strategy="steps",
        load_best_model_at_end=True if val_dataset else False,
        report_to="tensorboard" if config['logging'].get('use_tensorboard') else "none",
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=default_data_collator,
    )
    
    # Start training
    print("\nStarting fine-tuning...")
    print(f"Output directory: {config['logging']['output_dir']}")
    print(f"Training examples: {len(train_dataset)}")
    if val_dataset:
        print(f"Validation examples: {len(val_dataset)}")
    print(f"Epochs: {config['training']['num_epochs']}")
    print(f"Batch size: {config['data']['batch_size']}")
    print(f"Learning rate: {config['training']['learning_rate']}")
    print()
    
    trainer.train()
    
    # Save final model
    print("\nSaving final model...")
    trainer.save_model(os.path.join(config['logging']['output_dir'], 'final'))
    tokenizer.save_pretrained(os.path.join(config['logging']['output_dir'], 'final'))
    
    print("Fine-tuning complete!")


if __name__ == '__main__':
    main()
