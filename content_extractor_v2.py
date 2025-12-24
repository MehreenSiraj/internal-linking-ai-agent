"""
Content extraction from HTML with proper error handling and validation.
Designed for production use with comprehensive logging.
"""

import logging
from typing import Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentExtractionError(Exception):
    """Raised when content extraction fails."""
    pass


def extract_content(html: str) -> str:
    """
    Extract main text content from HTML, removing nav, footer, scripts.
    
    Args:
        html: HTML content as string
        
    Returns:
        Cleaned text content
        
    Raises:
        ContentExtractionError: If extraction fails
    """
    if not html or not isinstance(html, str):
        raise ContentExtractionError("HTML must be non-empty string")
    
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Remove unwanted elements
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'head']):
            tag.decompose()
        
        # Extract text
        text = soup.get_text(separator=" ", strip=True)
        
        # Clean up whitespace
        text = " ".join(text.split())
        
        if not text:
            logger.warning("Extracted empty content from HTML")
            raise ContentExtractionError("No content extracted from HTML")
        
        logger.debug(f"Extracted {len(text)} characters of content")
        return text
        
    except ContentExtractionError:
        raise
    except Exception as e:
        raise ContentExtractionError(f"Content extraction failed: {str(e)}")
