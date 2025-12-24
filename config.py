"""
Configuration management for Internal Linking AI Agent.
Production-grade centralized settings with validation.
"""

import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


@dataclass
class CrawlerConfig:
    """Configuration for website crawler.
    
    Attributes:
        max_pages: Maximum pages to crawl
        request_timeout: Timeout for HTTP requests in seconds
        min_delay: Minimum delay between requests in seconds
        max_delay: Maximum delay between requests in seconds
        user_agent: User agent string for requests
        retry_attempts: Number of retry attempts for failed requests
    """
    max_pages: int = 100
    request_timeout: int = 10
    min_delay: float = 0.5
    max_delay: float = 2.0
    user_agent: str = "Mozilla/5.0 (SEO-Agent/1.0) Compatible"
    retry_attempts: int = 3

    def __post_init__(self) -> None:
        """Validate crawler configuration."""
        if self.max_pages < 1:
            raise ValueError("max_pages must be >= 1")
        if self.request_timeout < 1:
            raise ValueError("request_timeout must be >= 1")
        if self.min_delay < 0:
            raise ValueError("min_delay must be >= 0")
        if self.max_delay <= self.min_delay:
            raise ValueError("max_delay must be > min_delay")
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be >= 0")


@dataclass
class ContentConfig:
    """Configuration for content processing.
    
    Attributes:
        min_content_words: Minimum words for valid content
        max_embedding_chars: Maximum characters for embedding
    """
    min_content_words: int = 200
    max_embedding_chars: int = 2000

    def __post_init__(self) -> None:
        """Validate content configuration."""
        if self.min_content_words < 1:
            raise ValueError("min_content_words must be >= 1")
        if self.max_embedding_chars < 1:
            raise ValueError("max_embedding_chars must be >= 1")


@dataclass
class ClusteringConfig:
    """Configuration for semantic clustering.
    
    Attributes:
        min_clusters: Minimum number of clusters
        max_clusters: Maximum number of clusters
        min_silhouette_score: Minimum acceptable silhouette score
        kmeans_init: K-means initialization method
        kmeans_seed: Random seed for reproducibility
        model_name: Sentence transformer model name
    """
    min_clusters: int = 2
    max_clusters: int = 15
    min_silhouette_score: float = 0.2
    kmeans_init: str = "k-means++"
    kmeans_seed: int = 42
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    def __post_init__(self) -> None:
        """Validate clustering configuration."""
        if self.min_clusters < 2:
            raise ValueError("min_clusters must be >= 2")
        if self.max_clusters < self.min_clusters:
            raise ValueError("max_clusters must be >= min_clusters")
        if not -1 <= self.min_silhouette_score <= 1:
            raise ValueError("min_silhouette_score must be between -1 and 1")


@dataclass
class LinkingConfig:
    """Configuration for internal link planning.
    
    Attributes:
        utility_keywords: Keywords identifying utility pages
        min_pillar_words: Minimum words for pillar page
        min_anchor_words: Minimum anchor text words
        max_anchor_words: Maximum anchor text words
        min_anchor_overlap: Minimum word overlap required
        max_links_per_page: Maximum links per page per topic
    """
    utility_keywords: List[str] = field(default_factory=lambda: [
        "privacy", "terms", "cookie", "disclaimer",
        "contact", "login", "signup", "404", "about",
        "legal", "policy", "sitemap"
    ])
    min_pillar_words: int = 300
    min_anchor_words: int = 2
    max_anchor_words: int = 5
    min_anchor_overlap: int = 2
    max_links_per_page: int = 1

    def __post_init__(self) -> None:
        """Validate linking configuration."""
        if self.min_pillar_words < 1:
            raise ValueError("min_pillar_words must be >= 1")
        if self.min_anchor_words < 1:
            raise ValueError("min_anchor_words must be >= 1")
        if self.max_anchor_words < self.min_anchor_words:
            raise ValueError("max_anchor_words must be >= min_anchor_words")
        if self.min_anchor_overlap < 1:
            raise ValueError("min_anchor_overlap must be >= 1")
        if self.max_links_per_page < 1:
            raise ValueError("max_links_per_page must be >= 1")


@dataclass
class OutputConfig:
    """Configuration for output generation.
    
    Attributes:
        output_dir: Output directory path
        csv_filename_pattern: CSV filename pattern
        pdf_filename_pattern: PDF filename pattern
        json_filename_pattern: JSON filename pattern
    """
    output_dir: Path = field(default_factory=lambda: Path("."))
    csv_filename_pattern: str = "{domain}_{timestamp}_links.csv"
    pdf_filename_pattern: str = "{domain}_{timestamp}_report.pdf"
    json_filename_pattern: str = "{domain}_{timestamp}_metadata.json"


@dataclass
class LoggingConfig:
    """Configuration for logging.
    
    Attributes:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Logging message format
        log_file: Optional log file path
    """
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Path = None

    def __post_init__(self) -> None:
        """Validate logging configuration."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level not in valid_levels:
            raise ValueError(f"level must be one of {valid_levels}")


class Config:
    """Central configuration management with validation.
    
    This class aggregates all configuration sections and provides
    methods for serialization and validation. All modifications
    should go through this class to ensure consistency.
    """
    
    def __init__(self) -> None:
        """Initialize configuration with all subsections."""
        self.crawler = CrawlerConfig()
        self.content = ContentConfig()
        self.clustering = ClusteringConfig()
        self.linking = LinkingConfig()
        self.output = OutputConfig()
        self.logging = LoggingConfig()
        
        # Validate on initialization
        self.validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of all configuration
        """
        return {
            "crawler": asdict(self.crawler),
            "content": asdict(self.content),
            "clustering": asdict(self.clustering),
            "linking": asdict(self.linking),
            "output": {k: str(v) if isinstance(v, Path) else v 
                      for k, v in asdict(self.output).items()},
            "logging": asdict(self.logging),
        }
    
    def validate(self) -> None:
        """Validate all configuration sections.
        
        Raises:
            ValueError: If any configuration is invalid
        """
        try:
            # Validate each config section (calls __post_init__)
            self.crawler.__post_init__()
            self.content.__post_init__()
            self.clustering.__post_init__()
            self.linking.__post_init__()
            self.logging.__post_init__()
            logger.debug("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise


# Global config instance
config = Config()
