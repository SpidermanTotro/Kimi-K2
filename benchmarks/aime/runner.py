"""
AIME Benchmark Runner
THE FORGE AI - Phase 2: Benchmark Optimization

Implements testing infrastructure for AIME (AI Math Evaluation) benchmark.
Target: 6-15% improvement over baseline (69.6%)
"""

import json
import time
from typing import Dict, List
from datetime import datetime

from openai import OpenAI


class AIMERunner:
    """Runner for AIME evaluation."""
    
    def __init__(self, config: Dict, client: OpenAI):
        """Initialize AIME runner."""
        self.config = config['benchmarks']['aime']
        self.model_config = config['model']
        self.client = client
        self.baseline_score = 69.6  # From README evaluation results (AIME 2024, Avg@64)
        
    def run(self) -> Dict:
        """Run AIME evaluation."""
        print("Loading AIME problems...")
        problems = self._load_problems()
        
        results = {
            'total_tests': len(problems),
            'passed': 0,
            'failed': 0,
            'test_results': [],
            'baseline_score': self.baseline_score,
            'year': self.config.get('year', 2024)
        }
        
        print(f"Running {len(problems)} AIME problems...")
        for i, problem in enumerate(problems, 1):
            print(f"  Problem {i}/{len(problems)}: {problem['id']}")
            
            test_result = self._run_problem(problem)
            results['test_results'].append(test_result)
            
            if test_result['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        results['pass_rate'] = (results['passed'] / results['total_tests']) * 100
        results['improvement_over_baseline'] = results['pass_rate'] - self.baseline_score
        
        return results
    
    def _load_problems(self) -> List[Dict]:
        """Load AIME problems.
        
        In a full implementation, this would load from the actual AIME dataset.
        For now, we provide a framework with sample problems.
        """
        # Sample problems - in production, load from actual benchmark
        return [
            {
                'id': 'AIME_2024_I_1',
                'problem': 'Find the number of positive integers less than 1000 that can be expressed as the difference of two integral powers of 2.',
                'answer': '340',
                'difficulty': 'medium'
            },
            {
                'id': 'AIME_2024_I_2',
                'problem': 'Let S be the set of all positive integers n such that n^2 + 19n + 92 is a perfect square. What is the sum of all elements in S?',
                'answer': '15',
                'difficulty': 'medium'
            },
            {
                'id': 'AIME_2024_I_3',
                'problem': 'A rectangular box has integer side lengths in the ratio 1:3:4. Which of the following could be the volume of the box? (A) 48 (B) 56 (C) 64 (D) 96 (E) 144',
                'answer': '96',
                'difficulty': 'easy'
            },
            # Add more problems here
        ]
    
    def _run_problem(self, problem: Dict) -> Dict:
        """Run a single AIME problem."""
        start_time = time.time()
        
        try:
            # Create prompt for problem solving
            prompt = self._create_prompt(problem)
            
            # Get model response
            response = self.client.chat.completions.create(
                model=self.model_config['name'],
                messages=[
                    {"role": "system", "content": "You are an expert mathematician. Solve the problem step-by-step and provide the final answer as a number."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.model_config['temperature'],
                max_tokens=self.model_config['max_tokens']
            )
            
            solution = response.choices[0].message.content
            
            # Extract answer and validate
            extracted_answer = self._extract_answer(solution)
            passed = self._validate_answer(problem['answer'], extracted_answer)
            
            elapsed_time = time.time() - start_time
            
            return {
                'id': problem['id'],
                'passed': passed,
                'expected': problem['answer'],
                'got': extracted_answer,
                'solution': solution,
                'elapsed_time': elapsed_time
            }
            
        except Exception as e:
            return {
                'id': problem['id'],
                'passed': False,
                'error': str(e),
                'elapsed_time': time.time() - start_time
            }
    
    def _create_prompt(self, problem: Dict) -> str:
        """Create prompt for problem solving."""
        prompt = f"""
AIME Problem {problem['id']}:

{problem['problem']}

Please solve this problem step-by-step, showing your work clearly.
At the end, provide your final answer in the format: ANSWER: <number>
"""
        return prompt
    
    def _extract_answer(self, solution: str) -> str:
        """Extract numerical answer from solution text."""
        # Look for "ANSWER:" or "Final Answer:" patterns
        import re
        
        patterns = [
            r'ANSWER:\s*(\d+)',
            r'Final Answer:\s*(\d+)',
            r'answer is\s*(\d+)',
            r'=\s*(\d+)\s*$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, solution, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)
        
        # If no pattern found, try to extract last number in text
        numbers = re.findall(r'\b(\d+)\b', solution)
        if numbers:
            return numbers[-1]
        
        return ""
    
    def _validate_answer(self, expected: str, got: str) -> bool:
        """Validate if the answer is correct."""
        # Normalize answers (remove whitespace, convert to string)
        expected_norm = str(expected).strip()
        got_norm = str(got).strip()
        
        return expected_norm == got_norm
