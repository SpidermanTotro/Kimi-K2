#!/usr/bin/env python3
"""
Data Augmentation Tools for Kimi K2

This module provides various data augmentation techniques to generate
synthetic training data for improving model performance.
"""

import json
import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataAugmentor:
    """Data augmentation toolkit for training data generation."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the data augmentor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.techniques = {
            'paraphrase': self._paraphrase,
            'back_translate': self._back_translate,
            'noise_injection': self._noise_injection,
            'template_based': self._template_based,
            'adversarial': self._adversarial
        }
    
    def augment(
        self,
        data: List[Dict],
        techniques: List[str],
        augmentation_factor: int = 2,
        preserve_original: bool = True
    ) -> List[Dict]:
        """Augment training data.
        
        Args:
            data: List of training examples
            techniques: List of augmentation techniques to apply
            augmentation_factor: Number of augmented samples per original
            preserve_original: Whether to include original samples
            
        Returns:
            List of augmented training examples
        """
        logger.info(f"Augmenting {len(data)} examples with techniques: {techniques}")
        
        augmented = []
        
        if preserve_original:
            augmented.extend(data)
        
        for example in data:
            for _ in range(augmentation_factor):
                # Randomly select a technique
                technique = random.choice(techniques)
                
                # Apply augmentation
                if technique in self.techniques:
                    augmented_example = self.techniques[technique](example)
                    if augmented_example:
                        augmented.append(augmented_example)
        
        logger.info(f"Generated {len(augmented)} total examples")
        return augmented
    
    def _paraphrase(self, example: Dict) -> Dict:
        """Generate paraphrased version of the example.
        
        Args:
            example: Original training example
            
        Returns:
            Paraphrased example
        """
        # Placeholder implementation
        # In production, use a paraphrasing model
        augmented = example.copy()
        
        # Simple word substitutions as placeholder
        input_text = example.get('input', '')
        substitutions = {
            'What is': 'Can you explain what',
            'How do': 'Could you tell me how to',
            'Why': 'What is the reason that',
        }
        
        for old, new in substitutions.items():
            if old in input_text:
                input_text = input_text.replace(old, new, 1)
                break
        
        augmented['input'] = input_text
        augmented['augmentation'] = 'paraphrase'
        
        return augmented
    
    def _back_translate(self, example: Dict) -> Dict:
        """Generate back-translated version.
        
        Args:
            example: Original training example
            
        Returns:
            Back-translated example
        """
        # Placeholder implementation
        # In production, use translation models
        augmented = example.copy()
        augmented['augmentation'] = 'back_translate'
        
        # Would translate to intermediate language and back
        # For now, just mark it
        
        return augmented
    
    def _noise_injection(self, example: Dict) -> Dict:
        """Inject controlled noise into the example.
        
        Args:
            example: Original training example
            
        Returns:
            Noisy example
        """
        augmented = example.copy()
        input_text = example.get('input', '')
        
        # Add minor typos (simple placeholder)
        words = input_text.split()
        if len(words) > 3:
            # Randomly swap two adjacent characters in a word
            idx = random.randint(0, len(words) - 1)
            word = words[idx]
            if len(word) > 2:
                pos = random.randint(0, len(word) - 2)
                word_list = list(word)
                word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
                words[idx] = ''.join(word_list)
        
        augmented['input'] = ' '.join(words)
        augmented['augmentation'] = 'noise_injection'
        
        return augmented
    
    def _template_based(self, example: Dict) -> Dict:
        """Generate example using templates.
        
        Args:
            example: Original training example
            
        Returns:
            Template-based example
        """
        augmented = example.copy()
        
        # Simple template variations
        templates = [
            "I need help with: {input}",
            "Question: {input}",
            "Could you assist me with {input}",
        ]
        
        template = random.choice(templates)
        augmented['input'] = template.format(input=example.get('input', ''))
        augmented['augmentation'] = 'template_based'
        
        return augmented
    
    def _adversarial(self, example: Dict) -> Dict:
        """Generate adversarial example.
        
        Args:
            example: Original training example
            
        Returns:
            Adversarial example
        """
        augmented = example.copy()
        
        # Simple adversarial modification
        # In production, use adversarial generation techniques
        input_text = example.get('input', '')
        
        # Add challenging modifiers
        modifiers = [
            "In simple terms, ",
            "Explain like I'm five: ",
            "From a technical perspective, ",
        ]
        
        modifier = random.choice(modifiers)
        augmented['input'] = modifier + input_text
        augmented['augmentation'] = 'adversarial'
        
        return augmented
    
    def save_augmented_data(self, data: List[Dict], output_path: str):
        """Save augmented data to file.
        
        Args:
            data: Augmented data
            output_path: Output file path
        """
        with open(output_path, 'w') as f:
            for example in data:
                f.write(json.dumps(example) + '\n')
        
        logger.info(f"Saved {len(data)} examples to {output_path}")


def main():
    """Example usage of data augmentation."""
    # Sample data
    data = [
        {
            "input": "What is machine learning?",
            "output": "Machine learning is a subset of AI..."
        },
        {
            "input": "How do neural networks work?",
            "output": "Neural networks are computing systems..."
        }
    ]
    
    # Create augmentor
    augmentor = DataAugmentor()
    
    # Augment data
    augmented = augmentor.augment(
        data=data,
        techniques=['paraphrase', 'noise_injection', 'template_based'],
        augmentation_factor=3
    )
    
    # Save results
    augmentor.save_augmented_data(augmented, 'augmented_data.jsonl')
    
    print(f"Generated {len(augmented)} augmented examples")


if __name__ == "__main__":
    main()
