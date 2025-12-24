from collections import defaultdict

def build_semantic_clusters(pages, labels):
    clusters = defaultdict(list)

    for page, label in zip(pages, labels):
        clusters[label].append(page)

    return clusters
