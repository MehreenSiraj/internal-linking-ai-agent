# ARCHITECTURE: SEO Internal Linking AI Agent

## System Overview

Production-grade system for generating semantic internal linking recommendations using sentence transformers and K-means clustering.

### Core Pipeline
```
Website → Crawl → Extract Content → Cluster Semantically → Plan Links → Output
```

## How to Run

### Basic Usage
```bash
python run_agent.py --site https://example.com
```

### Output Options
```bash
# Skip PDF (faster)
python run_agent.py --site https://example.com --no-pdf

# JSON only (automation)
python run_agent.py --site https://example.com --json-only

# For n8n webhook integration
python run_agent.py --site https://example.com --n8n-mode

# Debug mode (verbose logging)
python run_agent.py --site https://example.com --debug
```

### Return Value
```python
{
    "site": "https://example.com",
    "total_pages": 25,
    "usable_pages": 18,
    "recommendations_count": 12,
    "recommendations": [
        {
            "source_url": "https://example.com/page1",
            "target_url": "https://example.com/page2",
            "anchor": "keyword phrase",
            "semantic_score": "0.75"
        }
    ],
    "quality_score": "0.65",
    "execution_time_seconds": "45.32",
    "errors": [],
    "success": true,
    "timestamp": "2024-12-24T15:30:45.123456"
}
```

## How to Deploy

### VPS Deployment (Linux/Ubuntu)

#### 1. SSH into Server
```bash
ssh user@your-vps-ip
cd /opt/seo-agent
```

#### 2. Install Python 3.8+
```bash
sudo apt-get update
sudo apt-get install python3.8 python3.8-venv python3-pip
```

#### 3. Clone Repository
```bash
git clone https://github.com/MehreenSiraj/internal-linking-ai-agent.git
cd internal-linking-ai-agent
```

#### 4. Create Virtual Environment
```bash
python3.8 -m venv venv
source venv/bin/activate
```

#### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 6. Test Installation
```bash
python run_agent.py --site https://mehreensiraj.com --no-pdf
```

#### 7. Setup Cron Job (Daily at 2 AM)
```bash
crontab -e
# Add line:
0 2 * * * cd /opt/seo-agent && source venv/bin/activate && python run_agent.py --site https://your-site.com >> logs/daily_run.log 2>&1
```

#### 8. Setup n8n Webhook (Optional)
```bash
# Create webhook endpoint in n8n
# Point to: https://your-server:port/webhook/seo-agent

# Update run_agent.py with:
# python run_agent.py --site {site} --n8n-mode | curl -X POST https://n8n-instance/webhook
```

### Docker Deployment
```bash
# Build image
docker build -t seo-agent .

# Run container
docker run -v $(pwd)/outputs:/app/outputs seo-agent --site https://example.com
```

### GitHub Actions (Automated Testing)
See `.github/workflows/tests.yml` for CI/CD pipeline.

## How to Debug

### 1. Enable Debug Logging
```bash
python run_agent.py --site https://example.com --debug
```

**Output Levels:**
- `DEBUG` - Detailed diagnostic info (model loading, parsing details)
- `INFO` - General flow (crawled X pages, found Y clusters)
- `WARNING` - Unexpected but recoverable (failed to extract content)
- `ERROR` - Errors affecting functionality (timeout, validation failed)
- `CRITICAL` - System unusable (complete pipeline failure)

### 2. Check Logs

```bash
# View real-time logs
tail -f seo_agent.log

# Search for errors
grep ERROR seo_agent.log

# Show last 100 lines
tail -100 seo_agent.log
```

### 3. Common Issues

#### Issue: "No pages crawled"
```bash
# Check network connectivity
curl -I https://your-site.com

# Verify site structure
curl https://your-site.com/sitemap.xml

# Check crawl debug output
python run_agent.py --site https://your-site.com --debug 2>&1 | grep -i crawl
```

#### Issue: "Low silhouette score"
```
Means clusters aren't well-separated semantically
Solution: Ensure pages cover different topics (not all similar)
```

#### Issue: "No links generated"
```
Possible causes:
1. Pages too similar (all same topic)
2. Anchor overlap threshold too high
3. All pages marked as utility pages

Check: python run_agent.py --debug --site ... | grep -i utility
```

#### Issue: Timeout Errors
```bash
# Increase timeout in config.py:
# config.crawler.request_timeout = 20  (from 10)

# Or add rate-limiting:
# config.crawler.min_delay = 2.0  (from 0.5)
```

### 4. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | grep -E "sentence-transformers|scikit-learn|beautifulsoup4"

# Test imports
python -c "from crawler_v2 import crawl_pages; print('✓ Crawler OK')"
python -c "from semantic_topics_v2 import SemanticClusterer; print('✓ Clustering OK')"
python -c "from config import config; print('✓ Config OK')"

# Type check
mypy run_agent.py --strict
```

### 5. Test with Sample Data

```bash
# Quick test (small site)
python run_agent.py --site https://example.com --no-pdf

# Full test with all outputs
python run_agent.py --site https://example.com

# JSON only (no PDF generation)
python run_agent.py --site https://example.com --json-only

# Debug test
python run_agent.py --site https://example.com --debug --no-pdf
```

## Code Standards

### Type Hints (100%)
All functions have complete type annotations:
```python
def process(data: List[str]) -> Dict[str, int]:
    """Process data."""
    pass
```

### Error Handling
Specific exceptions with logging (no bare except):
```python
try:
    result = requests.get(url)
except requests.exceptions.Timeout:
    logger.error(f"Timeout: {url}")
except Exception as e:
    logger.critical(f"Error: {e}")
```

### Configuration
Centralized, validated settings:
```python
from config import config
timeout = config.crawler.request_timeout  # Not hardcoded
```

### Logging
Professional logging framework:
```python
logger.info("Starting crawl")
logger.warning("Low quality clustering")
logger.error("Failed to extract content")
```

### Documentation
Google-style docstrings on all public functions:
```python
def function(param: str) -> bool:
    """Brief description.
    
    Longer description if needed.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
        
    Raises:
        ValueError: When validation fails
    """
```

## Module Reference

### Core Modules
| Module | Purpose | Key Class/Function |
|--------|---------|-------------------|
| `run_agent.py` | Main orchestration | `run(site: str) -> AgentResult` |
| `crawler_v2.py` | Website crawling | `crawl_pages(site: str) -> CrawlResult` |
| `content_extractor_v2.py` | HTML parsing | `extract_content(html: str) -> str` |
| `semantic_topics_v2.py` | ML clustering | `SemanticClusterer.cluster_pages()` |
| `internal_link_planner_v2.py` | Link generation | `plan_semantic_links()` |
| `output_writer_v2.py` | File output | `write_csv()`, `write_json()` |
| `config.py` | Configuration | `config` (global instance) |
| `url_utils_v2.py` | URL utilities | `normalize_url()`, `validate_url()` |

### Configuration Sections

#### Crawler Config
```python
config.crawler.max_pages         # 100 (pages to crawl)
config.crawler.min_delay         # 0.5 (seconds between requests)
config.crawler.max_delay         # 2.0 (seconds between requests)
config.crawler.request_timeout   # 10 (request timeout)
```

#### Clustering Config
```python
config.clustering.min_clusters       # 2 (minimum clusters)
config.clustering.max_clusters       # 15 (maximum clusters)
config.clustering.min_silhouette_score  # 0.2 (quality threshold)
config.clustering.model_name         # "sentence-transformers/all-MiniLM-L6-v2"
```

#### Linking Config
```python
config.linking.utility_keywords   # Keywords to exclude (privacy, terms, etc.)
config.linking.min_anchor_overlap # 2 (word overlap required)
config.linking.max_links_per_page # 1 (per topic)
```

### Exception Hierarchy

```
Exception
├── CrawlerError              (Crawling failures)
├── ContentExtractionError    (HTML parsing failures)
├── ClusteringError           (Semantic analysis failures)
├── LinkPlanningError         (Link generation failures)
├── OutputError               (File writing failures)
├── URLError                  (URL processing failures)
└── AgentError                (Pipeline orchestration failures)
```

## Safety Constraints

1. **Utility Page Filtering** - Excludes privacy, terms, contact, etc. (13 keywords)
2. **Anchor Validation** - Requires 2+ word semantic overlap with target
3. **Cluster Size** - Enforces 2-15 clusters (prevents over/under-clustering)
4. **Rate Limiting** - Random 0.5-2 second delays between requests
5. **Self-Link Prevention** - Never links a page to itself
6. **Duplicate Prevention** - Max 1 link per page per topic

## Testing

```bash
# Run all unit tests
pytest test_internal_linking.py -v

# Run specific test
pytest test_internal_linking.py::TestFunctionName -v

# Type checking
mypy run_agent.py --strict

# Lint
pylint run_agent.py
```

**Current Status**: 17/17 tests passing (100%)

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Crawl (100 pages) | 2-5 min | Rate-limited to 0.5-2s delays |
| Extract content | <1s | Per-page, concurrent possible |
| Clustering | 30-60s | Depends on page count and model |
| Link planning | 5-10s | Depends on recommendations count |
| PDF generation | 5-15s | Detailed report with charts |
| **Total** | **3-8 min** | For typical 50-page site |

## File Structure

```
internal_links_ai-agent/
├── run_agent.py              # Production entrypoint
├── crawler_v2.py             # Website crawling
├── content_extractor_v2.py   # HTML parsing
├── semantic_topics_v2.py     # ML clustering
├── internal_link_planner_v2.py  # Link generation
├── output_writer_v2.py       # File output
├── semantic_graph_v2.py      # Cluster analysis
├── url_utils_v2.py           # URL utilities
├── pdf_report.py             # PDF generation
├── config.py                 # Configuration
├── test_internal_linking.py  # Unit tests
├── requirements.txt          # Dependencies
├── README.md                 # User guide
├── DEPLOYMENT.md             # Deployment guide
├── ARCHITECTURE.md           # This file
├── QUICK_START_REFACTORING.md # Dev quickstart
└── _legacy/                  # Archived v1 modules
    ├── crawler.py
    ├── run_agent.py
    └── ...other v1 modules
```

## Dependencies

**Core Libraries:**
- `sentence-transformers` - Semantic embeddings
- `scikit-learn` - K-means clustering
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP client
- `pandas` - Data processing
- `reportlab` - PDF generation
- `nltk` - NLP (POS tagging)

**Dev Tools:**
- `pytest` - Unit testing
- `mypy` - Type checking
- `pylint` - Linting
- `black` - Code formatting
- `bandit` - Security scanning

## Version History

```
v2.0 (Current)  - Production-grade with type hints, error handling, logging
v1.0 (Legacy)   - Prototype version (archived in _legacy/)
```

## Support

### Quick Questions
- Check `QUICK_START_REFACTORING.md` for getting started
- Check `README.md` for user-facing documentation

### Deployment Issues
- See "How to Deploy" section above
- Check deployment logs: `tail -f seo_agent.log`

### Code/Architecture Questions
- See module reference above
- Review inline code comments and docstrings
- Check `test_internal_linking.py` for usage examples

### Contributing
All code must follow CODE_STANDARDS.md:
- 100% type hints
- Specific exception handling
- Professional logging
- Google-style docstrings
- Comprehensive unit tests

---

**Last Updated**: December 24, 2025
**Version**: 2.0 (Production)
**Status**: Enterprise-Ready
