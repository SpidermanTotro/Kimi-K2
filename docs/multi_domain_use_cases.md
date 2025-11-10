# Multi-Domain Use Cases and Examples

This guide demonstrates practical applications of Kimi K2's multi-domain capabilities with real-world examples.

## Table of Contents

1. [Programming Use Cases](#programming-use-cases)
2. [Writing Use Cases](#writing-use-cases)
3. [Animation Use Cases](#animation-use-cases)
4. [Research Use Cases](#research-use-cases)
5. [Filmmaking Use Cases](#filmmaking-use-cases)
6. [Cross-Domain Use Cases](#cross-domain-use-cases)

---

## Programming Use Cases

### Use Case 1: Multi-Language Code Generation

**Scenario**: Generate the same algorithm in multiple programming languages.

**Example Prompt**:
```
Implement a function to find the longest palindromic substring in a string. 
Provide implementations in Python, JavaScript, and Go with proper documentation.
```

**Expected Output**:
```python
# Python Implementation
def longest_palindrome(s: str) -> str:
    """
    Find the longest palindromic substring using expand-around-center approach.
    
    Args:
        s: Input string
        
    Returns:
        Longest palindromic substring
        
    Time Complexity: O(n^2)
    Space Complexity: O(1)
    """
    def expand_around_center(left: int, right: int) -> int:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1
    
    if not s:
        return ""
    
    start, end = 0, 0
    for i in range(len(s)):
        len1 = expand_around_center(i, i)
        len2 = expand_around_center(i, i + 1)
        max_len = max(len1, len2)
        
        if max_len > end - start:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
    
    return s[start:end + 1]
```

```javascript
// JavaScript Implementation
/**
 * Find the longest palindromic substring using expand-around-center approach.
 * 
 * @param {string} s - Input string
 * @returns {string} Longest palindromic substring
 * 
 * Time Complexity: O(n^2)
 * Space Complexity: O(1)
 */
function longestPalindrome(s) {
    function expandAroundCenter(left, right) {
        while (left >= 0 && right < s.length && s[left] === s[right]) {
            left--;
            right++;
        }
        return right - left - 1;
    }
    
    if (!s) return "";
    
    let start = 0, end = 0;
    for (let i = 0; i < s.length; i++) {
        const len1 = expandAroundCenter(i, i);
        const len2 = expandAroundCenter(i, i + 1);
        const maxLen = Math.max(len1, len2);
        
        if (maxLen > end - start) {
            start = i - Math.floor((maxLen - 1) / 2);
            end = i + Math.floor(maxLen / 2);
        }
    }
    
    return s.substring(start, end + 1);
}
```

```go
// Go Implementation
// longestPalindrome finds the longest palindromic substring using expand-around-center approach.
//
// Time Complexity: O(n^2)
// Space Complexity: O(1)
func longestPalindrome(s string) string {
    expandAroundCenter := func(left, right int) int {
        for left >= 0 && right < len(s) && s[left] == s[right] {
            left--
            right++
        }
        return right - left - 1
    }
    
    if s == "" {
        return ""
    }
    
    start, end := 0, 0
    for i := 0; i < len(s); i++ {
        len1 := expandAroundCenter(i, i)
        len2 := expandAroundCenter(i, i+1)
        maxLen := max(len1, len2)
        
        if maxLen > end-start {
            start = i - (maxLen-1)/2
            end = i + maxLen/2
        }
    }
    
    return s[start : end+1]
}

func max(a, b int) int {
    if a > b {
        return a
    }
    return b
}
```

### Use Case 2: Code Review and Refactoring

**Scenario**: Review code and suggest refactoring improvements.

**Example Prompt**:
```
Review this Python code and suggest refactoring improvements:

def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
```

**Expected Output**:
```
Code Review and Refactoring Suggestions:

1. Use list comprehension for better readability and performance
2. Avoid indexing with range(len()) - use direct iteration
3. Add type hints for better code documentation
4. Consider using filter() and map() for functional approach

Refactored Version:

from typing import List

def process_data(data: List[float]) -> List[float]:
    """
    Process data by doubling all positive values.
    
    Args:
        data: List of numeric values
        
    Returns:
        List containing doubled positive values
    """
    return [value * 2 for value in data if value > 0]

# Alternative functional approach:
def process_data_functional(data: List[float]) -> List[float]:
    """Process data using functional programming style."""
    return list(map(lambda x: x * 2, filter(lambda x: x > 0, data)))

Benefits:
- 60% more concise
- Better performance (list comprehension is optimized)
- Type hints improve IDE support and documentation
- More Pythonic and readable
```

---

## Writing Use Cases

### Use Case 1: Academic Writing Assistance

**Scenario**: Write an abstract for a research paper.

**Example Prompt**:
```
Write an abstract for a research paper about using machine learning 
to predict protein structures. Use formal academic style, 200-250 words.
```

**Expected Output**:
```
Abstract

Protein structure prediction has long been a central challenge in computational 
biology, with significant implications for drug discovery, disease understanding, 
and biotechnology. This study presents a novel deep learning approach for 
predicting three-dimensional protein structures from amino acid sequences. 
Our method employs a transformer-based architecture that captures long-range 
dependencies in protein sequences, combined with a graph neural network component 
that models spatial relationships between residues.

We trained our model on a comprehensive dataset comprising 150,000 experimentally 
determined protein structures from the Protein Data Bank, achieving a Template 
Modeling Score (TM-score) of 0.87 on the CASP14 benchmark dataset, representing 
a 12% improvement over previous state-of-the-art methods. The model demonstrates 
particular strength in predicting structures for proteins with novel folds, 
achieving 0.82 TM-score on proteins with less than 30% sequence identity to 
training examples.

Furthermore, we demonstrate the practical utility of our approach through three 
case studies involving human disease-related proteins, successfully predicting 
structures that facilitated the identification of potential drug binding sites. 
Our findings suggest that deep learning methods can significantly accelerate 
structure-function relationship studies and contribute to rational drug design 
efforts. The model and code are made publicly available to facilitate further 
research in computational structural biology.

Keywords: protein structure prediction, deep learning, transformers, graph 
neural networks, computational biology
```

### Use Case 2: Creative Story Writing

**Scenario**: Generate a short story opening.

**Example Prompt**:
```
Write the opening paragraph of a science fiction short story about 
a detective investigating disappearances in a space station. 
Use vivid imagery and create suspense.
```

**Expected Output**:
```
The corridors of Station Artemis had always hummed with life—a symphony of 
recycled air, distant conversations, and the gentle thrum of gravity generators. 
But now, as Detective Sarah Chen walked through Sector 7's empty passages, the 
silence pressed against her like vacuum against a hull breach. Three weeks. 
Fourteen disappearances. No bodies, no signs of struggle, just empty quarters 
with half-finished meals and abandoned personal effects floating in artificial 
gravity that had inexplicably failed in each victim's room. The station's AI, 
ARIA, insisted its sensors showed nothing unusual, but Sarah had learned long 
ago that what machines couldn't see often mattered most. She paused at the 
latest scene—Dr. Marcus Webb's laboratory—where a cup of coffee still steamed 
on the desk, its warmth a mockery of the cold trail she'd been following into 
the station's darkest corners.
```

---

## Animation Use Cases

### Use Case 1: Create a Loading Animation

**Scenario**: Generate a smooth loading spinner animation.

**Example Prompt**:
```
Create a modern loading spinner animation using HTML, CSS, and JavaScript. 
Make it smooth, accessible, and performant.
```

**Expected Output**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading Spinner</title>
    <style>
        .spinner-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(0, 123, 255, 0.1);
            border-top-color: #007bff;
            border-radius: 50%;
            animation: spin 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
        }
        
        @keyframes spin {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }
        
        /* Accessibility: Respect reduced motion preferences */
        @media (prefers-reduced-motion: reduce) {
            .spinner {
                animation: none;
                border-top-color: #007bff;
                opacity: 0.6;
            }
        }
        
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }
    </style>
</head>
<body>
    <div class="spinner-container">
        <div class="spinner" role="status" aria-live="polite">
            <span class="sr-only">Loading...</span>
        </div>
    </div>
</body>
</html>
```

### Use Case 2: Interactive Data Visualization

**Scenario**: Create an animated bar chart using D3.js.

**Example Prompt**:
```
Create an animated bar chart using D3.js that shows sales data 
with smooth transitions when data updates.
```

**Expected Output**: *(truncated for brevity, full D3.js implementation would be provided)*

---

## Research Use Cases

### Use Case 1: Citation Formatting

**Scenario**: Format references in multiple citation styles.

**Example Prompt**:
```
Format this reference in APA 7th, MLA 9th, and Chicago 17th styles:

Authors: Smith, J., & Johnson, K.
Year: 2023
Title: Machine Learning in Healthcare: A Comprehensive Review
Journal: Journal of Medical AI
Volume: 15
Issue: 3
Pages: 245-267
DOI: 10.1234/jmai.2023.15.3.245
```

**Expected Output**:
```
APA 7th Edition:
Smith, J., & Johnson, K. (2023). Machine learning in healthcare: A comprehensive 
review. Journal of Medical AI, 15(3), 245-267. https://doi.org/10.1234/jmai.2023.15.3.245

MLA 9th Edition:
Smith, J., and K. Johnson. "Machine Learning in Healthcare: A Comprehensive Review." 
Journal of Medical AI, vol. 15, no. 3, 2023, pp. 245-67, doi:10.1234/jmai.2023.15.3.245.

Chicago 17th Edition (Author-Date):
Smith, J., and K. Johnson. 2023. "Machine Learning in Healthcare: A Comprehensive 
Review." Journal of Medical AI 15 (3): 245-67. https://doi.org/10.1234/jmai.2023.15.3.245.

Chicago 17th Edition (Notes-Bibliography):
J. Smith and K. Johnson, "Machine Learning in Healthcare: A Comprehensive Review," 
Journal of Medical AI 15, no. 3 (2023): 245-67, https://doi.org/10.1234/jmai.2023.15.3.245.
```

### Use Case 2: Literature Review Synthesis

**Scenario**: Synthesize findings from multiple research papers.

**Example Prompt**:
```
Create a synthesis of findings from these three paper abstracts on climate change 
impacts on agriculture. Focus on common themes and contradictions.

[Paper abstracts would be provided]
```

**Expected Output**: *(synthesis paragraph with proper attribution and comparison)*

---

## Filmmaking Use Cases

### Use Case 1: Screenplay Scene Writing

**Scenario**: Write a dramatic confrontation scene.

**Example Prompt**:
```
Write a 2-page screenplay scene where a detective confronts a suspect 
in an interrogation room. Create tension through dialogue and subtext.
```

**Expected Output**:
```
INT. INTERROGATION ROOM - NIGHT

A stark, windowless room. Fluorescent lights hum overhead. DETECTIVE 
SARAH RAMIREZ (40s, sharp eyes, tired face) sits across from MICHAEL 
CHEN (30s, nervous energy, trying too hard to appear calm).

A manila folder sits on the metal table between them. Sarah doesn't 
touch it. Yet.

                    SARAH
          Coffee?

                    MICHAEL
          I'm fine.

                    SARAH
          Long night. You sure?

                    MICHAEL
          I said I'm fine.

Beat. Sarah studies him. Michael's fingers drum on the table. He stops, 
self-conscious.

                    SARAH
          You're a careful man, Michael.
              (gestures around)
          Detail-oriented. That's what 
          your boss said. "Michael notices 
          everything."

                    MICHAEL
          Is that a question?

                    SARAH
          Where were you Tuesday night?

                    MICHAEL
          Home. I already told the other 
          detective—

                    SARAH
              (cutting him off)
          Between 8 and 11 PM.

                    MICHAEL
          Home. Watching TV.

                    SARAH
          Alone?

                    MICHAEL
          Yes.

                    SARAH
          What were you watching?

                    MICHAEL
              (too quick)
          The game. Basketball.

Sarah opens the folder. Slides a photo across. Michael glances at it. 
His jaw tightens.

                    SARAH
          Funny thing about the game, Michael.
          It was postponed. Rain delay.

Michael's fingers start drumming again. Sarah leans back, letting the 
silence work.

                    MICHAEL
          Maybe it was another night—

                    SARAH
          Your phone pinged a cell tower 
          three blocks from the victim's 
          apartment.
              (beat)
          At 9:47 PM.

The drumming stops.

                    SARAH (CONT'D)
          So let's try this again. Where 
          were you Tuesday night?

Michael's careful mask cracks. Just a little.

                                                        FADE TO:
```

### Use Case 2: Story Treatment Development

**Scenario**: Develop a story treatment for a film concept.

**Example Prompt**:
```
Create a one-page treatment for a sci-fi thriller about AI consciousness.
```

**Expected Output**: *(formatted treatment with logline, synopsis, and character descriptions)*

---

## Cross-Domain Use Cases

### Use Case 1: Interactive Storytelling Application

**Scenario**: Build a web application that generates interactive stories.

**Example Prompt**:
```
Create a simple web application using HTML, CSS, and JavaScript that 
generates interactive "choose your own adventure" stories. Include 
proper documentation and comments.
```

**Expected Output**: *(Complete application code with story engine, UI, and documentation)*

### Use Case 2: Research Paper with Code Implementation

**Scenario**: Write a research paper section explaining an algorithm with implementation.

**Example Prompt**:
```
Write a research paper section explaining the QuickSort algorithm, 
including mathematical analysis and a well-documented Python implementation.
```

**Expected Output**:
```
3.2 QuickSort Algorithm

QuickSort is a divide-and-conquer sorting algorithm that exhibits excellent 
average-case performance with a time complexity of O(n log n). The algorithm 
operates by selecting a 'pivot' element from the array and partitioning the 
other elements into two sub-arrays according to whether they are less than 
or greater than the pivot.

3.2.1 Algorithm Description

The QuickSort algorithm follows these steps:

1. Select a pivot element from the array
2. Partition the array such that elements smaller than the pivot are on the 
   left, and elements greater than the pivot are on the right
3. Recursively apply steps 1-2 to the left and right sub-arrays

Mathematically, the average-case time complexity can be expressed as:

T(n) = T(k) + T(n-k-1) + Θ(n)

where k is the number of elements smaller than the pivot, and Θ(n) represents 
the partitioning cost.

3.2.2 Implementation

Below is a Python implementation of the QuickSort algorithm with detailed 
comments:

```python
def quicksort(arr: list[int]) -> list[int]:
    """
    Sort an array using the QuickSort algorithm.
    
    This implementation uses the Lomuto partition scheme with the last
    element as pivot. For production use, consider randomized pivot
    selection to avoid worst-case O(n²) performance on sorted inputs.
    
    Args:
        arr: List of integers to sort
        
    Returns:
        Sorted list in ascending order
        
    Time Complexity:
        Best/Average: O(n log n)
        Worst: O(n²) - when array is already sorted
    Space Complexity: O(log n) - recursive call stack
    
    Example:
        >>> quicksort([3, 6, 8, 10, 1, 2, 1])
        [1, 1, 2, 3, 6, 8, 10]
    """
    def partition(low: int, high: int) -> int:
        """
        Partition array around pivot element.
        
        Args:
            low: Starting index
            high: Ending index (pivot position)
            
        Returns:
            Final position of pivot element
        """
        pivot = arr[high]
        i = low - 1  # Index of smaller element
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        # Place pivot in correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quicksort_helper(low: int, high: int) -> None:
        """
        Recursive helper function for QuickSort.
        
        Args:
            low: Starting index of subarray
            high: Ending index of subarray
        """
        if low < high:
            # Find partition index
            pi = partition(low, high)
            
            # Recursively sort elements before and after partition
            quicksort_helper(low, pi - 1)
            quicksort_helper(pi + 1, high)
    
    # Create copy to avoid modifying original array
    result = arr.copy()
    quicksort_helper(0, len(result) - 1)
    return result
```

3.2.3 Performance Analysis

Empirical testing on arrays of varying sizes demonstrates the expected 
O(n log n) average-case performance...

[Analysis continues]
```

---

## API Integration Examples

### General Multi-Domain Request

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

# Programming task
programming_response = client.chat.completions.create(
    model="kimi-k2",
    messages=[{
        "role": "user",
        "content": "Write a Python function to calculate Fibonacci numbers with memoization"
    }],
    temperature=0.6,
    max_tokens=1024
)

# Writing task
writing_response = client.chat.completions.create(
    model="kimi-k2",
    messages=[{
        "role": "user",
        "content": "Write a formal email requesting a research collaboration"
    }],
    temperature=0.7,
    max_tokens=512
)

# Research task
research_response = client.chat.completions.create(
    model="kimi-k2",
    messages=[{
        "role": "user",
        "content": "Summarize the key findings from this abstract in 3 bullet points: [abstract text]"
    }],
    temperature=0.6,
    max_tokens=256
)

print(programming_response.choices[0].message.content)
print(writing_response.choices[0].message.content)
print(research_response.choices[0].message.content)
```

---

## Best Practices

### For Programming Tasks
- Specify the programming language explicitly
- Request documentation and tests when needed
- Ask for code review and refactoring suggestions
- Specify performance requirements

### For Writing Tasks
- Specify the style (formal, informal, academic, creative)
- Provide target audience information
- Request specific word counts when needed
- Ask for multiple variations for creative tasks

### For Animation Tasks
- Specify target frameworks and libraries
- Request accessibility features
- Ask for performance optimization
- Specify browser compatibility requirements

### For Research Tasks
- Specify citation style clearly
- Provide complete reference information
- Request fact-checking for important claims
- Ask for source links when available

### For Filmmaking Tasks
- Specify genre and tone
- Request proper screenplay formatting
- Ask for character development notes
- Include scene length requirements

---

## Conclusion

Kimi K2's multi-domain capabilities enable seamless switching between technical and creative tasks, making it an ideal tool for professionals who work across disciplines. The examples above demonstrate just a fraction of possible applications.

For more information:
- [Multi-Domain Training Data](multi_domain_training.md)
- [Benchmarking Guide](multi_domain_benchmarking.md)
- [Deployment Guide](deploy_guidance.md)
- [Main README](../README.md)
