"""
URL utilities for normalization and validation.
Production-grade with error handling.
"""

import logging
from typing import Optional
from urllib.parse import urljoin, urlparse, urlunparse

logger = logging.getLogger(__name__)


class URLError(Exception):
    """Raised when URL processing fails."""
    pass


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent comparison and storage.
    Removes fragments, normalizes scheme and host.
    
    Args:
        url: URL string to normalize
        
    Returns:
        Normalized URL
        
    Raises:
        URLError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise URLError("URL must be non-empty string")
    
    try:
        # Parse URL
        parsed = urlparse(url.strip())
        
        # Ensure scheme
        if not parsed.scheme:
            parsed = urlparse("http://" + url)
        
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            parsed.params,
            parsed.query,
            ""  # Remove fragment
        ))
        
        return normalized
        
    except Exception as e:
        raise URLError(f"Failed to normalize URL '{url}': {str(e)}")


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        return all([
            parsed.scheme in ["http", "https"],
            parsed.netloc
        ])
    except Exception:
        return False


def get_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain/hostname
        
    Raises:
        URLError: If domain extraction fails
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        raise URLError(f"Failed to extract domain from '{url}': {str(e)}")


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs belong to same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if same domain, False otherwise
    """
    try:
        domain1 = get_domain(url1)
        domain2 = get_domain(url2)
        return domain1 == domain2
    except URLError:
        return False


def absolute_url(relative: str, base: str) -> Optional[str]:
    """
    Convert relative URL to absolute using base URL.
    
    Args:
        relative: Relative URL
        base: Base URL
        
    Returns:
        Absolute URL or None if conversion fails
    """
    try:
        absolute = urljoin(base, relative)
        return normalize_url(absolute)
    except Exception as e:
        logger.warning(f"Failed to convert '{relative}' relative to '{base}': {e}")
        return None
