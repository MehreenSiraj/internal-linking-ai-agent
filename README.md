# Internal Linking AI Agent (SEO-Safe, Production-Ready)

A production-ready Internal Linking AI Agent that analyzes a website,
identifies contextual internal linking opportunities, and generates
professional recommendations (CSV + PDF).

This system **does NOT modify websites automatically**.
It is designed for **SEO safety**, **manual control**, and **professional use**.

---

## 🔍 What This Agent Does

1. **Crawls** all internal pages of a given website (with rate-limiting)
2. **Extracts** clean, meaningful content (no nav/footer/script noise)
3. **Analyzes** semantic similarity using sentence transformers
4. **Clusters** pages by topic using K-means with silhouette validation
5. **Identifies** pillar pages (comprehensive, non-utility pages)
6. **Finds** natural contextual link opportunities using POS-tagged noun phrases
7. **Validates** anchors against target page content (2+ word semantic overlap)
8. **Generates** professional reports (CSV + PDF)

---

## 🛡️ What This Agent Does NOT Do

- ❌ No automatic changes to any CMS
- ❌ No auto-insertion of links
- ❌ No CMS credentials required
- ❌ No JavaScript-based DOM manipulation
- ❌ No keyword stuffing
- ❌ No links from utility pages (privacy, terms, contact)

**Safe for:**
- Client audits
- Portfolio demonstrations
- Agency workflows
- SEO experiments

---

## 🧠 Why Internal Linking Matters

Internal linking improves:
- **Crawlability**: Helps search engines discover pages
- **Indexation Speed**: Signals page importance
- **Topical Authority**: Reinforces topic clusters (pillar → supporting)
- **Link Equity Distribution**: Flows PageRank through site structure
- **Rankings**: Often drives ranking improvements within weeks

This agent focuses on **contextual, semantic links**, not random keyword stuffing.

---

## 🏗️ Architecture Overview

```
User Website URL
    ↓
Website Crawler (with rate-limiting)
    ↓
Content Extraction (removes noise)
    ↓
Semantic Embeddings (sentence-transformers)
    ↓
Clustering & Pillar Identification
    ↓
Anchor Extraction (POS tagging, validation)
    ↓
CSV + PDF Report
```

**Integration with n8n:**
```
WordPress Form
    ↓
n8n Webhook
    ↓
Python Agent (this repo)
    ↓
Timestamped CSV/PDF/JSON Output
```

---

## 📁 Project Structure

```
internal_links_ai-agent/
│
├── run_agent.py                 # Main entry point (handles n8n + CLI)
├── crawler.py                   # Crawls all internal pages
├── content_extractor.py         # Cleans & extracts page content
├── semantic_topics.py           # Embeddings + clustering
├── semantic_graph.py            # Cluster grouping
├── internal_link_planner.py     # Link planning logic (safety rules)
├── output_writer.py             # CSV output (dynamic filenames)
├── pdf_report.py                # Professional PDF generation
├── url_utils.py                 # URL normalization
│
├── test_internal_linking.py     # Comprehensive test suite (17 tests)
├── requirements.txt             # Dependencies
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/internal-linking-ai-agent.git
cd internal-linking-ai-agent
```

### 2. Create virtual environment (optional)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

Dependencies installed:
- **requests** / **beautifulsoup4** / **lxml**: Web scraping
- **pandas**: Data handling
- **sentence-transformers**: Semantic embeddings
- **scikit-learn**: K-means clustering + silhouette scoring
- **nltk**: POS tagging for anchor extraction
- **reportlab**: PDF generation

---

## 🚀 Usage

### CLI Usage (Local Development)

**Basic run:**
```bash
python run_agent.py --site https://example.com
```

**Output:**
```
============================================================
Internal Linking Analysis: https://example.com
============================================================
Status: SUCCESS
Pages crawled: 47
Usable content pages: 34
Clusters: 5
Cohesion score: 0.423
Links recommended: 12

[!] Warnings:
  • Low cluster cohesion (0.159). Results may be less topically relevant.

[OK] Outputs:
  • csv: example_com_20251224_180212_links.csv
  • pdf: example_com_20251224_180212_report.pdf
  • metadata: example_com_20251224_180212_metadata.json
============================================================
```

**Advanced options:**
```bash
# Skip PDF generation (faster for testing)
python run_agent.py --site https://example.com --skip-pdf

# JSON output only (for n8n integration)
python run_agent.py --site https://example.com --json-output

# CSV only
python run_agent.py --site https://example.com --format csv
```

---

### n8n Integration

Add a **webhook node** in n8n to call the agent:

```bash
curl -X POST http://your-vps:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"site": "https://example.com"}'
```

The agent responds with JSON:
```json
{
  "status": "success",
  "site": "https://example.com",
  "timestamp": "2025-12-24T18:02:12.188405",
  "warnings": [],
  "metadata": {
    "total_pages_crawled": 47,
    "usable_pages": 34,
    "num_clusters": 5,
    "silhouette_score": 0.423,
    "num_links_recommended": 12
  },
  "outputs": {
    "csv": "example_com_20251224_180212_links.csv",
    "pdf": "example_com_20251224_180212_report.pdf",
    "metadata": "example_com_20251224_180212_metadata.json"
  }
}
```

---

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_internal_linking.py
```

**Tests included (17 total):**
- ✅ Utility page detection (privacy, terms, contact, cookie, login)
- ✅ Anchor validation (must exist in target, semantic overlap ≥2 words)
- ✅ Pillar identification (longest non-utility page per cluster)
- ✅ Link generation safety (no self-links, no utility page sources)
- ✅ Cluster quality (silhouette score calculation)
- ✅ Output format (CSV structure, no duplicates)

**Expected output:**
```
Ran 17 tests in 2.101s
OK
```

---

## 📊 Understanding the Output

### CSV Format
```
from,to,anchor,sentence
https://example.com/page-a,https://example.com/page-b,"anchor text","Full sentence context..."
```

- **from**: Source page (where the link will be added)
- **to**: Target page (where the link points)
- **anchor**: Exact text to use as link (already exists on source page)
- **sentence**: Context (for verification)

### PDF Report
Professional, client-ready document including:
- Executive summary
- Methodology explanation
- Cluster cohesion metrics
- Detailed recommendations table
- Implementation guide

### Metadata JSON
```json
{
  "status": "success",
  "site": "https://example.com",
  "timestamp": "2025-12-24T18:02:12.188405",
  "metadata": {
    "total_pages_crawled": 47,
    "usable_pages": 34,
    "num_clusters": 5,
    "silhouette_score": 0.423,
    "num_links_recommended": 12
  },
  "warnings": [],
  "errors": []
}
```

---

## 🔒 Safety Guarantees

This system enforces strict SEO safety:

1. **No Utility Pages**: Links never originate from privacy, terms, contact, cookie, login pages
2. **Anchor Validation**: Anchors must have 2+ word semantic overlap with target
3. **No Self-Links**: Pages never link to themselves
4. **Max 1 Link Per Topic**: Only one link per source page per cluster
5. **Semantic Basis**: Links reinforce topical authority, not random keywords
6. **POS-Filtered Anchors**: Only grammatically sound noun phrases extracted
7. **Cluster Validation**: Silhouette score shows topical cohesion
8. **Manual Control**: All recommendations require human approval before implementation

---

## 🚢 Deployment (VPS + n8n)

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Step 1: Clone on VPS
```bash
cd /var/www
git clone https://github.com/yourusername/internal-linking-ai-agent.git
cd internal-linking-ai-agent
```

### Step 2: Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Create Wrapper Script (for n8n)
Save as `agent.sh`:
```bash
#!/bin/bash
cd /var/www/internal-linking-ai-agent
source venv/bin/activate
python run_agent.py --site "$1" --json-output
```

Make executable:
```bash
chmod +x agent.sh
```

### Step 4: Configure n8n
In n8n, create a webhook that calls:
```bash
/var/www/internal-linking-ai-agent/agent.sh https://example.com
```

### Step 5: Output Management
Set up cron job to archive old outputs:
```bash
# Archive outputs older than 30 days
0 2 * * * find /var/www/internal-linking-ai-agent -name "*_links.csv" -mtime +30 -exec gzip {} \;
```

---

## 📈 Performance Notes

- **Crawl time**: ~30 sec - 5 min depending on site size (includes rate-limiting)
- **Embedding time**: ~5-30 sec depending on page count
- **PDF generation**: ~2-5 sec
- **Total pipeline**: 1-10 minutes for typical sites

For large sites (200+ pages), consider running overnight or in batches.

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: nltk` | Run `pip install -r requirements.txt` |
| `No pages crawled` | Check site URL, firewall, robots.txt |
| `Only 1 usable page` | Site may have thin content (<200 words) |
| `Low silhouette score (< 0.3)` | Pages may be poorly topically organized |
| `No links recommended` | Pages may be too similar or under-linked |
| `PDF generation fails` | Check write permissions in output directory |

---

## 🤝 Contributing

This is a production system. Before submitting changes:

1. Run the test suite: `python test_internal_linking.py`
2. Test locally: `python run_agent.py --site https://yoursite.com`
3. Verify CSV, PDF, and JSON outputs
4. Check error handling with invalid URLs

---

## 📝 License

This project is built for professional SEO automation. Use it responsibly.

---

## 🎯 Roadmap

- [ ] Database storage of historical reports
- [ ] Competitor analysis module
- [ ] A/B testing suggestions
- [ ] Bulk site analysis
- [ ] WordPress plugin wrapper
- [ ] REST API (FastAPI)

---

## 📧 Support

Questions? Issues?
- Check troubleshooting section
- Review test suite for expected behavior
- Check logs in `.log` files

---

**Built with ❤️ for SEO professionals who respect the web.**

pip install -r requirements.txt

▶️ How to Run (Local Test)
python run_agent.py --site https://example.com

Output:

output/internal_links.csv

output/internal-linking-report.pdf

🔌 n8n Integration (Production Use)

This project is designed to be executed via n8n Execute Command.

Example n8n command:

python /opt/internal-linking-ai-agent/run_agent.py --site {{$json.site_url}}


This allows:

WordPress → n8n → Python execution

Automated report generation

Portfolio-safe backend processing

📄 Output Report Includes

Website overview

Total pages analyzed

Suggested internal links

Source page

Target page

Suggested anchor text

Context sentence

Implementation guidelines

🚦 SEO Safety Principles

Crawl limits enforced

Context-only anchors

Max link suggestions per page

No repeated anchors

Manual review encouraged

This agent follows white-hat SEO best practices.

🧩 Future Enhancements

AI-assisted anchor text selection

Page importance scoring

Topical authority mapping

Google Search Console integration

Ranking impact tracking

👤 Author

Built by Mehreen Siraj
SEO Automation & AI Systems

Portfolio: https://mehreensiraj.com

📜 License

MIT License
Use, modify, and adapt freely.


---

## ✅ What You Should Do Next (Exact Order)

1️⃣ Add these two files to your repo  
2️⃣ Commit & push to GitHub  
3️⃣ Clone repo on your VPS  
4️⃣ Install requirements on VPS  
5️⃣ Confirm `run_agent.py` runs on VPS  

👉 **Do NOT touch n8n again until step 5 is confirmed.**

---

When you’re ready, say **“repo pushed”**  
Next, I’ll:
- Review `run_agent.py`
- Add **crawl limits + robots respect**
- Design the **PDF layout (this matters a LOT)**




