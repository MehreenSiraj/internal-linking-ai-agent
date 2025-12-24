import argparse
import math
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

from crawler import crawl_pages
from content_extractor import extract_clean_text
from semantic_topics import embed_pages, cluster_pages
from semantic_graph import build_semantic_clusters
from internal_link_planner import plan_semantic_links
from output_writer import write_csv
from pdf_report import generate_pdf_report
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_output_filenames(site_url):
    """
    Generate timestamped output filenames for n8n integration.
    Allows multiple runs without overwriting previous results.
    """
    # Sanitize domain name
    domain = site_url.split("://")[-1].replace("www.", "").split("/")[0].replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    base_name = f"{domain}_{timestamp}"
    
    return {
        "csv": f"{base_name}_links.csv",
        "pdf": f"{base_name}_report.pdf",
        "json": f"{base_name}_metadata.json"
    }


def run(site, output_format="both", skip_pdf=False):
    """
    Main agent pipeline.
    
    Args:
        site: Website URL to analyze
        output_format: "csv" | "pdf" | "both" (default)
        skip_pdf: If True, skip PDF generation (faster for testing)
    
    Returns:
        Dict with status, output paths, and metadata
    """
    
    result = {
        "status": "error",
        "site": site,
        "timestamp": datetime.now().isoformat(),
        "errors": [],
        "warnings": [],
        "metadata": {},
        "outputs": {}
    }
    
    try:
        # 1. Crawl site
        logger.info(f"Crawling {site}...")
        crawled_pages = crawl_pages(site)
        result["metadata"]["total_pages_crawled"] = len(crawled_pages)
        logger.info(f"Crawled {len(crawled_pages)} pages")
        
        if len(crawled_pages) == 0:
            result["errors"].append("No pages crawled. Check site URL and network connectivity.")
            return result
        
        # 2. Extract clean content
        logger.info("Extracting clean content...")
        pages = []
        for p in crawled_pages:
            text = extract_clean_text(p["html"])
            
            # Skip thin pages (SEO-safe)
            if len(text.split()) < 200:
                continue
            
            pages.append({
                "url": p["url"],
                "content": text,
                "title": p.get("title", "")
            })
        
        result["metadata"]["usable_pages"] = len(pages)
        logger.info(f"Usable content pages: {len(pages)}")
        
        if len(pages) < 2:
            result["errors"].append(
                f"Only {len(pages)} usable pages found. Need at least 2 for linking analysis."
            )
            return result
        
        # 3. Create semantic embeddings
        logger.info("Computing semantic embeddings...")
        embeddings = embed_pages(pages)
        
        # 4. Decide number of clusters
        n_clusters = max(2, min(15, int(math.sqrt(len(pages)))))
        result["metadata"]["num_clusters"] = n_clusters
        logger.info(f"Computing {n_clusters} semantic clusters...")
        
        # 5. Cluster pages semantically
        labels, silhouette_avg = cluster_pages(embeddings, n_clusters)
        result["metadata"]["silhouette_score"] = float(silhouette_avg)
        logger.info(f"Cluster cohesion (silhouette score): {silhouette_avg:.3f}")
        
        if silhouette_avg < 0.2:
            result["warnings"].append(
                f"Low cluster cohesion ({silhouette_avg:.3f}). Results may be less topically relevant."
            )
        
        # 6. Build topical clusters
        clusters = build_semantic_clusters(pages, labels)
        
        # 7. Plan internal links
        logger.info("Planning internal links...")
        links = plan_semantic_links(clusters)
        result["metadata"]["num_links_recommended"] = len(links)
        logger.info(f"Generated {len(links)} link recommendations")
        
        # 8. Generate outputs
        filenames = generate_output_filenames(site)
        
        # Write CSV
        if output_format in ["csv", "both"]:
            logger.info(f"Writing CSV: {filenames['csv']}")
            csv_path = write_csv(links, output_file=filenames["csv"])
            result["outputs"]["csv"] = csv_path
        
        # Write PDF
        if output_format in ["pdf", "both"] and not skip_pdf:
            logger.info(f"Generating PDF: {filenames['pdf']}")
            links_df = pd.DataFrame(links)
            pdf_path = generate_pdf_report(
                links_df,
                site,
                output_path=filenames["pdf"],
                metadata=result["metadata"]
            )
            result["outputs"]["pdf"] = pdf_path
        
        # Write metadata
        result["outputs"]["metadata"] = filenames["json"]
        with open(filenames["json"], "w") as f:
            json.dump(result, f, indent=2)
        
        result["status"] = "success"
        logger.info("Pipeline completed successfully")
        
    except Exception as e:
        result["errors"].append(str(e))
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SEO-safe internal linking recommendation agent"
    )
    parser.add_argument("--site", required=True, help="Website URL to analyze")
    parser.add_argument(
        "--format",
        default="both",
        choices=["csv", "pdf", "both"],
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF generation (faster for testing)"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Print JSON output to stdout (for n8n integration)"
    )
    
    args = parser.parse_args()
    
    result = run(args.site, output_format=args.format, skip_pdf=args.skip_pdf)
    
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        # CLI output
        print(f"\n{'='*60}")
        print(f"Internal Linking Analysis: {args.site}")
        print(f"{'='*60}")
        print(f"Status: {result['status'].upper()}")
        print(f"Pages crawled: {result['metadata'].get('total_pages_crawled', 'N/A')}")
        print(f"Usable content pages: {result['metadata'].get('usable_pages', 'N/A')}")
        print(f"Clusters: {result['metadata'].get('num_clusters', 'N/A')}")
        print(f"Cohesion score: {result['metadata'].get('silhouette_score', 'N/A')}")
        print(f"Links recommended: {result['metadata'].get('num_links_recommended', 0)}")
        
        if result['warnings']:
            print(f"\n[!] Warnings:")
            for w in result['warnings']:
                print(f"  • {w}")
        
        if result['errors']:
            print(f"\n[ERROR] Errors:")
            for e in result['errors']:
                print(f"  • {e}")
        
        if result['outputs']:
            print(f"\n[OK] Outputs:")
            for key, path in result['outputs'].items():
                if path:
                    print(f"  • {key}: {path}")
        
        print(f"{'='*60}\n")
    
    # Exit with proper code
    sys.exit(0 if result['status'] == 'success' else 1)
