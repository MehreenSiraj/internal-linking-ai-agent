# Internal Linking AI Agent (SEO-Safe, Production-Ready)

A production-ready **Semantic Internal Linking AI Agent** that analyzes a website,
identifies contextual internal linking opportunities, and generates
**professional recommendations (CSV + PDF)**.

This system **does NOT modify websites automatically**.  
It is designed for **SEO safety**, **manual control**, and **professional use**.

---

## 🔍 What This Agent Does

1. Crawls all internal pages of a website (with rate-limiting)
2. Extracts clean, meaningful content (navigation/footer removed)
3. Generates semantic embeddings using sentence transformers
4. Clusters pages by topic (K-Means + silhouette validation)
5. Identifies pillar pages (authoritative, non-utility pages)
6. Finds contextual internal linking opportunities using noun phrases
7. Validates anchors against target page content (semantic overlap ≥ 2 words)
8. Produces **CSV + PDF** reports for human review

---

## 🛡️ What This Agent Does NOT Do

- ❌ No automatic CMS changes
- ❌ No auto-insertion of links
- ❌ No CMS credentials required
- ❌ No JavaScript DOM manipulation
- ❌ No keyword stuffing
- ❌ No links from utility pages (privacy, terms, contact, cookie)

Safe for:
- Client audits
- Agency workflows
- Portfolio demonstrations
- White-hat SEO analysis

---

## 🧠 Why Internal Linking Matters

Internal linking helps with:

- Crawlability & indexation
- Topical authority (pillar → supporting pages)
- Link equity distribution
- Clear site architecture
- Ranking improvements over time

This agent focuses on **semantic, contextual links**, not keyword spam.

---

## 🏗️ Architecture Overview

```

Website URL
↓
Crawler (rate-limited)
↓
Content Extraction
↓
Semantic Embeddings
↓
Clustering + Pillar Detection
↓
Anchor Extraction & Validation
↓
CSV + PDF Report

```

---

## 📁 Project Structure

```

internal_links_ai-agent/
│
├── run_agent.py
├── crawler.py
├── content_extractor.py
├── semantic_topics.py
├── semantic_graph.py
├── internal_link_planner.py
├── output_writer.py
├── pdf_report.py
├── url_utils.py
│
├── test_internal_linking.py
├── requirements.txt
└── README.md

````

---

## ⚙️ Installation

```bash
git clone https://github.com/MehreenSiraj/internal-linking-ai-agent.git
cd internal-linking-ai-agent
pip install -r requirements.txt
````

(Optional virtual environment recommended.)

---

## 🚀 Usage (Local)

```bash
python run_agent.py --site https://example.com
```

### Output

* CSV file with link recommendations
* PDF report (client-ready)

---

## 🧪 Testing

Run the test suite:

```bash
python test_internal_linking.py
```

All tests must pass before deployment.

---

## 🔒 SEO Safety Guarantees

* No utility pages used as link sources
* Anchors must exist in visible content
* Semantic validation enforced
* Max one link per page per topic
* Manual review required before implementation

---

## 🚢 Deployment (VPS + n8n – optional)

This project is designed to be triggered via **n8n Execute Command** or webhook
after validation in local or staging environments.

---

## 👤 Author

**Mehreen Siraj**
SEO Automation & AI Systems
Portfolio: [https://mehreensiraj.com](https://mehreensiraj.com)

---

## 📜 License

MIT License — use responsibly.