"""
Website crawler with rate-limiting and error handling.
Designed for production use with proper logging and validation.
"""

import logging
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from url_utils import normalize_url
from config import config

logger = logging.getLogger(__name__)


class CrawlerError(Exception):
    """Base exception for crawler errors."""
    pass


class CrawlResult:
    """Container for crawl results with metadata."""
    
    def __init__(self):
        self.pages: List[Dict[str, str]] = []
        self.errors: List[str] = []
        self.total_attempted: int = 0
        self.total_success: int = 0
        self.total_failed: int = 0


def validate_url(url: str) -> bool:
    """
    Validate URL format and accessibility.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception as e:
        logger.warning(f"URL validation failed for {url}: {e}")
        return False


def get_sitemap_urls(site: str) -> List[str]:
    """
    Extract URLs from sitemap.xml.
    
    Args:
        site: Website URL
        
    Returns:
        List of URLs from sitemap
    """
    sitemap_url = urljoin(site, "/sitemap.xml")
    urls = []

    try:
        logger.info(f"Fetching sitemap: {sitemap_url}")
        r = requests.get(
            sitemap_url,
            timeout=config.crawler.request_timeout,
            headers={"User-Agent": config.crawler.user_agent}
        )
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "xml")
        for loc in soup.find_all("loc"):
            url = normalize_url(loc.text)
            if validate_url(url):
                urls.append(url)
        
        logger.info(f"Found {len(urls)} URLs in sitemap")
        
    except requests.RequestException as e:
        logger.warning(f"Sitemap fetch failed: {e}")
    except Exception as e:
        logger.warning(f"Sitemap parsing failed: {e}")

    return list(set(urls))  # Deduplicate


def crawl_pages(site: str, limit: Optional[int] = None) -> CrawlResult:
    """
    Crawl all internal pages of a website.
    
    Args:
        site: Website URL to crawl
        limit: Maximum pages to crawl (default: config)
        
    Returns:
        CrawlResult with pages and metadata
        
    Raises:
        CrawlerError: If site validation fails
    """
    if not validate_url(site):
        raise CrawlerError(f"Invalid site URL: {site}")
    
    limit = limit or config.crawler.max_pages
    domain = urlparse(site).netloc
    visited = set()
    result = CrawlResult()
    
    logger.info(f"Starting crawl of {site} (max {limit} pages)")
    
    def crawl_recursive(url: str) -> None:
        """Recursively crawl pages with rate-limiting."""
        if url in visited or len(visited) >= limit:
            return
        
        visited.add(url)
        result.total_attempted += 1
        
        try:
            # Rate-limiting: random delay between requests
            delay = random.uniform(
                config.crawler.min_delay,
                config.crawler.max_delay
            )
            time.sleep(delay)
            
            logger.debug(f"Crawling: {url}")
            
            r = requests.get(
                url,
                timeout=config.crawler.request_timeout,
                headers={"User-Agent": config.crawler.user_agent}
            )
            r.raise_for_status()
            
            soup = BeautifulSoup(r.text, "lxml")
            
            result.pages.append({
                "url": url,
                "html": r.text,
                "title": soup.title.string if soup.title else ""
            })
            result.total_success += 1
            
            # Extract and crawl internal links
            for a in soup.select("a[href]"):
                link = normalize_url(urljoin(url, a["href"]))
                if urlparse(link).netloc == domain:
                    crawl_recursive(link)
        
        except requests.exceptions.Timeout:
            error_msg = f"Timeout crawling {url}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.total_failed += 1
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed for {url}: {str(e)}"
            logger.warning(error_msg)
            result.errors.append(error_msg)
            result.total_failed += 1
        
        except Exception as e:
            error_msg = f"Unexpected error crawling {url}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.total_failed += 1
    
    # Start crawling
    try:
        crawl_recursive(site)
    except KeyboardInterrupt:
        logger.info("Crawl interrupted by user")
    except Exception as e:
        raise CrawlerError(f"Crawl failed: {str(e)}")
    
    logger.info(
        f"Crawl complete: {result.total_success} successful, "
        f"{result.total_failed} failed out of {result.total_attempted} attempted"
    )
    
    return result
