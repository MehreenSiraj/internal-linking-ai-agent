# Code Standards and Best Practices

## Overview

This document defines the code standards and best practices for the SEO Internal Linking AI Agent. All code should adhere to these standards to maintain consistency, readability, and maintainability.

## 1. Type Hints

### Requirement
ALL functions and methods must have complete type hints for parameters and return values.

### Examples

```python
# ✅ Good: Complete type hints
def extract_content(html: str) -> str:
    """Extract text from HTML."""
    pass

def cluster_pages(pages: List[str]) -> Tuple[List[int], float]:
    """Cluster pages and return labels with score."""
    pass

# ❌ Bad: Missing type hints
def extract_content(html):
    """Extract text from HTML."""
    pass

def cluster_pages(pages):
    """Cluster pages."""
    pass
```

### Type Hint Checklist
- [ ] Function parameters have type hints
- [ ] Return types specified
- [ ] Optional parameters marked with Optional[]
- [ ] Complex types imported from typing module
- [ ] Type hints are accurate and specific

## 2. Error Handling

### Requirement
Never use bare `except:` statements. Always specify exception types and log errors.

### Pattern

```python
# ✅ Good: Specific exception handling
try:
    result = requests.get(url, timeout=10)
except requests.exceptions.Timeout:
    logger.error(f"Timeout: {url}")
except requests.exceptions.RequestException as e:
    logger.warning(f"Request failed: {e}")
except Exception as e:
    logger.critical(f"Unexpected error: {e}")

# ❌ Bad: Bare except silently fails
try:
    result = requests.get(url)
except:
    pass  # Silent failure!
```

### Custom Exceptions

Create specific exceptions for domain errors:

```python
# Define at module level
class CrawlerError(Exception):
    """Raised when crawling fails."""
    pass

class ContentExtractionError(Exception):
    """Raised when content extraction fails."""
    pass

# Use in functions
def crawl_pages(site: str) -> CrawlResult:
    """Crawl website pages.
    
    Raises:
        CrawlerError: If crawling fails critically
    """
    try:
        # ... implementation
    except CrawlerError:
        raise
    except Exception as e:
        raise CrawlerError(f"Crawling failed: {str(e)}")
```

## 3. Logging

### Requirement
Use Python's `logging` module consistently. No `print()` statements in production code.

### Setup

```python
import logging

# Create logger at module level
logger = logging.getLogger(__name__)

# Configure in application startup
def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(handler)
    
    return logger
```

### Logging Usage

```python
# INFO: General flow information
logger.info(f"Crawled {count} pages successfully")

# WARNING: Something unexpected but recoverable
logger.warning(f"Failed to extract from {url}, skipping")

# ERROR: Error that affects functionality
logger.error(f"Clustering failed: {error_message}")

# DEBUG: Detailed diagnostic information
logger.debug(f"Using model: {model_name}")

# CRITICAL: System is unusable
logger.critical(f"Configuration validation failed: {error}")
```

### Logging Best Practices

```python
# ✅ Good: Contextual information
logger.error(f"Failed to crawl {url}: timeout after {timeout}s")

# ❌ Bad: Vague error message
logger.error("Error")

# ✅ Good: Lazy string formatting
logger.debug("Processing page %s", url)  # Only formatted if debug is on

# ❌ Bad: Eager string formatting
logger.debug(f"Processing page {url}")  # Always formatted, even if not logged
```

## 4. Documentation

### Requirement
All public functions and classes must have Google-style docstrings.

### Format

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """
    Brief one-line description ending with period.
    
    Longer description if needed, explaining the purpose,
    behavior, and important implementation details.
    
    Args:
        param1: Description of param1 and its requirements
        param2: Description of param2, default 10
        
    Returns:
        Description of return value and its meaning
        
    Raises:
        ValueError: If param1 is empty
        RuntimeError: If processing fails
        
    Example:
        >>> result = function_name("input", 20)
        >>> assert result is True
    """
    if not param1:
        raise ValueError("param1 must not be empty")
    
    # Implementation
    return True
```

### Class Documentation

```python
class MyClass:
    """Brief class description.
    
    Longer description of the class purpose, use cases,
    and important behavior.
    
    Attributes:
        name: The object's name
        value: The object's value
    """
    
    def __init__(self, name: str, value: int):
        """Initialize MyClass.
        
        Args:
            name: The object's name
            value: The object's value
        """
        self.name = name
        self.value = value
```

### Dataclass Documentation

```python
@dataclass
class ConfigSection:
    """Configuration section for specific feature.
    
    Attributes:
        option1: Description of option1, default value
        option2: Description of option2, default value
    """
    option1: int = 100
    option2: str = "default"
```

## 5. Code Organization

### Module Structure

```python
"""
Module description - what does this module do?
How does it fit into the larger system?
"""

import logging
from typing import List, Dict, Optional

import external_library

from .local_module import function

# Module-level logger
logger = logging.getLogger(__name__)

# Custom exceptions
class ModuleError(Exception):
    """Raised when module operations fail."""
    pass

# Dataclasses/type definitions
@dataclass
class Result:
    """Result container."""
    data: List[str]

# Functions (ordered by dependency)
def helper_function() -> str:
    """Low-level utility function."""
    pass

def main_function(param: str) -> Result:
    """High-level business logic."""
    pass

# Runnable entry point
if __name__ == "__main__":
    # CLI entry point
    pass
```

### Import Organization

```python
# 1. Standard library
import logging
import os
from typing import List, Dict, Optional
from pathlib import Path

# 2. Third-party libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup

# 3. Local imports
from config import config
from utils import helper_function
```

## 6. Configuration Management

### Requirement
Use `config.py` dataclasses for all configuration. No hardcoded magic numbers.

### Pattern

```python
# ❌ Bad: Hardcoded value
def crawl_pages(site: str) -> List[str]:
    urls = []
    for i in range(100):  # Magic number!
        # ...

# ✅ Good: Use configuration
def crawl_pages(site: str) -> List[str]:
    urls = []
    for i in range(config.crawler.max_pages):
        # ...
```

### Configuration Access

```python
from config import config

# Access configuration
timeout = config.crawler.request_timeout
delay = random.uniform(config.crawler.min_delay, config.crawler.max_delay)
keywords = config.linking.utility_keywords

# Validate configuration (happens automatically on import)
config.validate()
```

## 7. Input Validation

### Requirement
Validate all inputs at function entry point.

### Pattern

```python
def process_data(items: List[str], threshold: int) -> None:
    """Process items above threshold.
    
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs FIRST
    if not items or not isinstance(items, list):
        raise ValueError("items must be non-empty list")
    
    if not isinstance(threshold, int) or threshold < 0:
        raise ValueError("threshold must be non-negative integer")
    
    # Now process with confidence
    for item in items:
        if len(item) >= threshold:
            # Process
            pass
```

### URL Validation

```python
from url_utils_v2 import validate_url, is_valid_url

def fetch_url(url: str) -> str:
    """Fetch content from URL.
    
    Raises:
        ValueError: If URL is invalid
    """
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")
    
    response = requests.get(url)
    return response.text
```

## 8. Naming Conventions

### Variables and Functions
- Use lowercase with underscores: `max_pages`, `crawl_pages()`
- Be descriptive: `processed_pages` not `pp`
- Use boolean prefixes: `is_valid`, `has_error`, `should_process`

```python
# ✅ Good
is_utility_page = True
max_retry_attempts = 3
def extract_noun_phrases(text: str) -> List[str]:
    pass

# ❌ Bad
utility_page = True  # Not clear if boolean
max_retry = 3  # "max" usually means number
def extract_np(text):  # Cryptic abbreviation
    pass
```

### Classes
- Use PascalCase: `CrawlResult`, `SemanticClusterer`
- Descriptive names: `LinkRecommendation` not `Rec`

```python
# ✅ Good
class CrawlResult:
    pass

class LinkRecommendation:
    pass

# ❌ Bad
class crawl_result:  # Should be PascalCase
    pass

class Rec:  # Too abbreviated
    pass
```

### Constants
- Use UPPERCASE_WITH_UNDERSCORES
- Define at module top level

```python
# ✅ Good
DEFAULT_TIMEOUT = 10
MIN_CLUSTER_SIZE = 2
UTILITY_KEYWORDS = ["privacy", "terms"]

# ❌ Bad
default_timeout = 10  # Should be uppercase for constants
minClusterSize = 2  # Should be snake_case
```

## 9. Testing

### Requirement
All public functions must have corresponding unit tests.

### Test Structure

```python
import pytest
from module_under_test import function

class TestFunctionName:
    """Tests for function_name."""
    
    def test_success_case(self):
        """Test function with valid input."""
        result = function("valid_input")
        assert result is not None
    
    def test_invalid_input(self):
        """Test function rejects invalid input."""
        with pytest.raises(ValueError):
            function("")
    
    def test_edge_case(self):
        """Test edge case behavior."""
        result = function("edge")
        assert result == "expected"
```

### Test Naming
- `test_<function>_<scenario>`
- `test_<function>_with_<condition>`
- `test_<function>_raises_<exception>`

```python
# ✅ Good test names
def test_extract_content_with_valid_html():
    pass

def test_extract_content_with_empty_html():
    pass

def test_extract_content_raises_error():
    pass

# ❌ Bad test names
def test_extract():  # Too vague
    pass

def test_1():  # Not descriptive
    pass
```

## 10. Performance Considerations

### Logging Performance

```python
# ❌ Bad: Expensive string formatting for every debug statement
logger.debug(f"Processing {expensive_function()}")

# ✅ Good: Lazy formatting, only done if DEBUG is on
logger.debug("Processing %s", expensive_function.__name__)
```

### Data Structures

```python
# ❌ Bad: Inefficient - checking if item in list (O(n))
urls_seen = []
if url not in urls_seen:
    urls_seen.append(url)

# ✅ Good: Set lookup is O(1)
urls_seen = set()
if url not in urls_seen:
    urls_seen.add(url)
```

### Clustering Optimization

```python
# ✅ Good: Cache embeddings for reuse
embeddings = model.encode(pages)  # Run once
# Use embeddings multiple times

# ❌ Bad: Recompute embeddings multiple times
for page in pages:
    emb1 = model.encode(page)  # Expensive!
    # ...
    emb2 = model.encode(page)  # Expensive again!
```

## 11. Security Best Practices

### Input Validation
```python
# Always validate URLs before processing
if not is_valid_url(user_input):
    raise ValueError("Invalid URL")

# Validate file paths
if not os.path.isfile(config.logging.log_file):
    Path(config.logging.log_file).parent.mkdir(exist_ok=True)
```

### Error Messages
```python
# ✅ Good: No sensitive information
raise ValueError("Invalid configuration")

# ❌ Bad: Exposes internal details
raise ValueError(f"Database password: {db_password}")
```

### Rate Limiting
```python
# Always include delays for external requests
import time
import random

delay = random.uniform(config.crawler.min_delay, config.crawler.max_delay)
time.sleep(delay)
request.get(url)
```

## Checklist for Code Review

### Every Pull Request Should Have:
- [ ] Type hints on all functions
- [ ] Docstrings with Args, Returns, Raises
- [ ] No bare `except:` statements
- [ ] Proper logging (not print statements)
- [ ] Input validation
- [ ] Configuration used (no hardcoded values)
- [ ] Unit tests for new functionality
- [ ] Error handling for edge cases
- [ ] Descriptive variable/function names
- [ ] Comments for complex logic

## Tools for Compliance

### Type Checking
```bash
mypy --strict *.py
```

### Code Formatting
```bash
black *.py
```

### Linting
```bash
pylint *.py
```

### Security Scanning
```bash
bandit *.py
```

### Testing
```bash
pytest test_*.py -v
```

## Resources

- [Python Type Hints - PEP 484](https://www.python.org/dev/peps/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Exception Handling - PEP 3151](https://www.python.org/dev/peps/pep-3151/)

---

**Version**: 1.0
**Last Updated**: 2024
**Owner**: Development Team
**Status**: ACTIVE - All new code must adhere to these standards
