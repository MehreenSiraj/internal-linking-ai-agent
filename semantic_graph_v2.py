"""
Semantic graph construction and cluster labeling.
Groups clusters by semantic similarity and assigns topic labels.
"""

import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


def group_clusters_by_topic(
    cluster_labels: List[int],
    semantic_scores: List[float]
) -> Dict[int, List[int]]:
    """
    Group page indices by cluster ID.
    
    Args:
        cluster_labels: Cluster assignment for each page
        semantic_scores: Semantic score for each page
        
    Returns:
        Dictionary mapping cluster ID to list of page indices
    """
    clusters: Dict[int, List[int]] = {}
    
    for page_idx, cluster_id in enumerate(cluster_labels):
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(page_idx)
    
    logger.debug(f"Grouped {len(cluster_labels)} pages into {len(clusters)} clusters")
    
    return clusters


def assign_cluster_labels(
    clusters: Dict[int, List[int]],
    page_titles: List[str]
) -> Dict[int, str]:
    """
    Assign semantic topic labels to clusters.
    
    Args:
        clusters: Dictionary mapping cluster ID to page indices
        page_titles: Page titles for each index
        
    Returns:
        Dictionary mapping cluster ID to topic label
    """
    labels: Dict[int, str] = {}
    
    for cluster_id, page_indices in clusters.items():
        # Get titles for pages in this cluster
        titles = [page_titles[idx] for idx in page_indices if idx < len(page_titles)]
        
        # Use longest/most descriptive title as label
        if titles:
            best_title = max(titles, key=len) if titles else f"Cluster {cluster_id}"
            # Truncate to reasonable length
            label = best_title[:60]
        else:
            label = f"Cluster {cluster_id}"
        
        labels[cluster_id] = label
        logger.debug(f"Cluster {cluster_id}: {label}")
    
    return labels
