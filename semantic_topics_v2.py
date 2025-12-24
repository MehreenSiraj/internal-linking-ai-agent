"""
Semantic page clustering with validation and error handling.
Uses sentence-transformers embeddings and K-means clustering with silhouette validation.
"""

import logging
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from config import config

logger = logging.getLogger(__name__)


class ClusteringError(Exception):
    """Raised when clustering fails."""
    pass


class SemanticClusterer:
    """Clusters pages by semantic content using embeddings."""
    
    def __init__(self):
        """Initialize the semantic clusterer with pre-trained model."""
        try:
            logger.info(f"Loading embedding model: {config.clustering.model_name}")
            self.model = SentenceTransformer(config.clustering.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            raise ClusteringError(f"Failed to load embedding model: {str(e)}")
    
    def cluster_pages(
        self,
        pages: List[str]
    ) -> Tuple[List[int], float]:
        """
        Cluster pages by semantic similarity.
        
        Args:
            pages: List of page contents as strings
            
        Returns:
            Tuple of (cluster labels, silhouette score)
            
        Raises:
            ClusteringError: If clustering fails or quality is poor
        """
        if not pages or len(pages) < 2:
            raise ClusteringError("Need at least 2 pages to cluster")
        
        try:
            logger.info(f"Generating embeddings for {len(pages)} pages")
            embeddings = self.model.encode(pages)
            logger.debug(f"Embeddings shape: {embeddings.shape}")
            
            # Determine optimal cluster count
            min_clusters = max(config.clustering.min_clusters, 2)
            max_clusters = min(
                config.clustering.max_clusters,
                len(pages)
            )
            
            logger.info(f"Cluster range: {min_clusters}-{max_clusters}")
            
            # Find best cluster count using silhouette score
            best_score = -1
            best_labels = None
            best_n = min_clusters
            
            for n_clusters in range(min_clusters, max_clusters + 1):
                try:
                    kmeans = KMeans(
                        n_clusters=n_clusters,
                        random_state=config.clustering.random_seed,
                        n_init=10
                    )
                    labels = kmeans.fit_predict(embeddings)
                    score = silhouette_score(embeddings, labels)
                    
                    logger.debug(f"n_clusters={n_clusters}, silhouette_score={score:.3f}")
                    
                    if score > best_score:
                        best_score = score
                        best_labels = labels
                        best_n = n_clusters
                
                except Exception as e:
                    logger.warning(f"Failed to evaluate {n_clusters} clusters: {e}")
                    continue
            
            if best_labels is None:
                raise ClusteringError("Could not compute valid clustering")
            
            logger.info(
                f"Optimal clustering: {best_n} clusters, "
                f"silhouette_score={best_score:.3f}"
            )
            
            # Validate silhouette score
            if best_score < config.clustering.min_silhouette_score:
                logger.warning(
                    f"Low silhouette score: {best_score:.3f} "
                    f"(threshold: {config.clustering.min_silhouette_score})"
                )
            
            return best_labels.tolist(), float(best_score)
            
        except ClusteringError:
            raise
        except Exception as e:
            raise ClusteringError(f"Clustering failed: {str(e)}")
