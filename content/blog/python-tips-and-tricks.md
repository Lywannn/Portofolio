---
title: "10 Python Tips That Will Make You a Better Developer"
date: 2025-04-15
tags: ["Python", "Tips", "Productivity"]
excerpt: "Python is full of elegant features that many developers overlook. Here are 10 tips and tricks that will level up your Python code today."
cover_image: ""
---

## 1. Use f-strings (Python 3.6+)

```python
name = "Alice"
age = 30

# Old way
print("Hello, %s. You are %d years old." % (name, age))

# Better
print(f"Hello, {name}. You are {age} years old.")
```

## 2. Walrus Operator `:=`

Assign and evaluate in a single expression:

```python
import re

text = "Hello, World!"
if match := re.search(r"\w+", text):
    print(match.group())
```

## 3. List Comprehensions

```python
# Instead of:
squares = []
for x in range(10):
    squares.append(x ** 2)

# Use:
squares = [x ** 2 for x in range(10)]
```

## 4. Dictionary Merging (Python 3.9+)

```python
defaults = {"color": "blue", "size": "medium"}
overrides = {"color": "red"}

merged = defaults | overrides
# {'color': 'red', 'size': 'medium'}
```

## 5. Unpacking

```python
first, *middle, last = [1, 2, 3, 4, 5]
# first=1, middle=[2,3,4], last=5
```

## 6. Context Managers

```python
# Always use with open() for files
with open("file.txt") as f:
    content = f.read()
# File is automatically closed
```

## 7. dataclasses

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
print(p)  # Point(x=1.0, y=2.0)
```

## 8. `enumerate()` instead of range(len())

```python
fruits = ["apple", "banana", "cherry"]

# Instead of:
for i in range(len(fruits)):
    print(i, fruits[i])

# Use:
for i, fruit in enumerate(fruits):
    print(i, fruit)
```

## 9. `zip()` for parallel iteration

```python
names = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 92]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

## 10. `pathlib` instead of `os.path`

```python
from pathlib import Path

p = Path("data") / "users" / "config.json"
if p.exists():
    content = p.read_text()
```

These small changes add up to significantly cleaner, more Pythonic code. Which one was new to you?
