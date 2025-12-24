import argparse
import math

from crawler import crawl_pages
from content_extractor import extract_clean_text
from semantic_topics import embed_pages, cluster_pages
from semantic_graph import build_semantic_clusters
from internal_link_planner import plan_semantic_links
from output_writer import write_csv


def run(site):
    # 1. Crawl site
    crawled_pages = crawl_pages(site)
    print(f"Crawled pages: {len(crawled_pages)}")

    # 2. Extract clean content
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

    print(f"Usable content pages: {len(pages)}")

    if len(pages) < 3:
        print("Not enough content pages to build semantic clusters.")
        return

    # 3. Create semantic embeddings
    embeddings = embed_pages(pages)

    # 4. Decide number of clusters (guardrailed to prevent over/under-clustering)
    n_clusters = max(2, min(15, int(math.sqrt(len(pages)))))
    print(f"Number of semantic clusters: {n_clusters}")

    # 5. Cluster pages semantically
    labels, silhouette_avg = cluster_pages(embeddings, n_clusters)
    print(f"Cluster cohesion (silhouette score): {silhouette_avg:.3f}")
    
    if silhouette_avg < 0.2:
        print("WARNING: Low cluster cohesion. Results may be less topically relevant.")


    # 6. Build topical clusters
    clusters = build_semantic_clusters(pages, labels)

    # 7. Plan internal links
    links = plan_semantic_links(clusters)

    # 8. Write output
    write_csv(links)

    print(f"Internal linking plan generated with {len(links)} links.")
    print("Output file: semantic_internal_linking_plan.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    args = parser.parse_args()

    run(args.site)
