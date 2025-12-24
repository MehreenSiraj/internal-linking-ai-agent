"""
Internal link planning with semantic clustering and POS-tagged anchor extraction.
Identifies pillar pages, utility page filtering, and validates anchor text.
Production-grade with comprehensive error handling and logging.
"""

import logging
import re
from typing import List, Dict, Optional, Tuple

import nltk
from nltk import pos_tag, word_tokenize

from config import config

logger = logging.getLogger(__name__)

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)


class LinkPlanningError(Exception):
    """Raised when link planning fails."""
    pass


class LinkRecommendation:
    """Container for a link recommendation."""
    
    def __init__(
        self,
        source_url: str,
        target_url: str,
        anchor: str,
        semantic_score: float
    ):
        self.source_url = source_url
        self.target_url = target_url
        self.anchor = anchor
        self.semantic_score = semantic_score
    
    def to_dict(self) -> Dict[str, str]:
        """Convert recommendation to dictionary."""
        return {
            "source_url": self.source_url,
            "target_url": self.target_url,
            "anchor": self.anchor,
            "semantic_score": f"{self.semantic_score:.2f}"
        }


def is_utility_page(url: str, title: str = "") -> bool:
    """
    Identify utility pages (privacy, terms, contact, etc).
    
    Args:
        url: Page URL
        title: Page title
        
    Returns:
        True if page is utility, False otherwise
    """
    combined = (url + " " + title).lower()
    
    for keyword in config.linking.utility_keywords:
        if keyword.lower() in combined:
            logger.debug(f"Identified utility page: {url}")
            return True
    
    return False


def extract_noun_phrases(text: str) -> List[str]:
    """
    Extract noun phrases using POS tagging.
    Falls back to regex if POS tagging fails.
    
    Args:
        text: Text to extract phrases from
        
    Returns:
        List of noun phrases (2-5 words)
    """
    if not text or not isinstance(text, str):
        return []
    
    try:
        # POS tagging approach
        words = word_tokenize(text.lower())
        pos_tags = pos_tag(words)
        
        phrases = []
        phrase = []
        
        for word, pos in pos_tags:
            if pos.startswith('NN'):  # Nouns
                phrase.append(word)
            else:
                if phrase:
                    phrases.append(" ".join(phrase))
                    phrase = []
        
        if phrase:
            phrases.append(" ".join(phrase))
        
        # Filter by length (2-5 words)
        phrases = [
            p for p in phrases
            if config.linking.min_anchor_words <= len(p.split()) <= config.linking.max_anchor_words
        ]
        
        logger.debug(f"POS extraction found {len(phrases)} phrases")
        return phrases
        
    except Exception as e:
        logger.warning(f"POS tagging failed, falling back to regex: {e}")
        return extract_noun_phrases_regex(text)


def extract_noun_phrases_regex(text: str) -> List[str]:
    """
    Regex fallback for noun phrase extraction.
    
    Args:
        text: Text to extract from
        
    Returns:
        List of potential noun phrases
    """
    try:
        # Match capitalized words (potential nouns)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}\b'
        phrases = re.findall(pattern, text)
        
        logger.debug(f"Regex extraction found {len(phrases)} phrases")
        return list(set(phrases))
        
    except Exception as e:
        logger.warning(f"Regex extraction failed: {e}")
        return []


def select_best_anchor(
    candidate_phrases: List[str],
    target_content: str
) -> Optional[str]:
    """
    Select best anchor from candidates based on overlap with target.
    Requires 2+ word semantic overlap with target content.
    
    Args:
        candidate_phrases: List of candidate anchor phrases
        target_content: Target page content
        
    Returns:
        Best anchor if valid, None otherwise
    """
    if not candidate_phrases or not target_content:
        return None
    
    target_words = set(target_content.lower().split())
    
    for phrase in candidate_phrases:
        phrase_words = set(phrase.lower().split())
        overlap = phrase_words & target_words
        
        # Check 2+ word overlap requirement
        if len(overlap) >= config.linking.min_anchor_overlap:
            logger.debug(
                f"Selected anchor '{phrase}' with {len(overlap)} word overlap"
            )
            return phrase
    
    logger.debug("No valid anchor found with sufficient overlap")
    return None


def plan_semantic_links(
    pages: List[Dict[str, str]],
    cluster_labels: List[int],
    silhouette_score: float
) -> List[Dict[str, str]]:
    """
    Generate semantic linking recommendations.
    
    Args:
        pages: List of page data dicts with url, html, title, content
        cluster_labels: Cluster assignment for each page
        silhouette_score: Quality metric of clustering
        
    Returns:
        List of link recommendation dicts
        
    Raises:
        LinkPlanningError: If planning fails
    """
    if not pages or len(pages) < 2:
        raise LinkPlanningError("Need at least 2 pages")
    
    if len(cluster_labels) != len(pages):
        raise LinkPlanningError("Cluster labels length mismatch")
    
    logger.info(f"Planning links for {len(pages)} pages, {len(set(cluster_labels))} clusters")
    
    recommendations = []
    source_to_target: Dict[str, set] = {}  # Track links to avoid duplicates
    
    try:
        # Group pages by cluster
        clusters: Dict[int, List[int]] = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)
        
        # Process each cluster
        for cluster_id, page_indices in clusters.items():
            if len(page_indices) < 2:
                logger.debug(f"Cluster {cluster_id} has <2 pages, skipping")
                continue
            
            logger.debug(f"Processing cluster {cluster_id} with {len(page_indices)} pages")
            
            # Find pillar page (longest, non-utility)
            pillar_idx = None
            pillar_length = 0
            
            for idx in page_indices:
                page = pages[idx]
                if not is_utility_page(page.get("url", ""), page.get("title", "")):
                    content_length = len(page.get("content", ""))
                    if content_length > pillar_length:
                        pillar_length = content_length
                        pillar_idx = idx
            
            if pillar_idx is None:
                logger.warning(f"No valid pillar page in cluster {cluster_id}")
                continue
            
            pillar = pages[pillar_idx]
            pillar_url = pillar.get("url", "")
            pillar_content = pillar.get("content", "")
            
            logger.debug(f"Pillar page for cluster {cluster_id}: {pillar_url}")
            
            # Generate links from other pages to pillar
            for idx in page_indices:
                if idx == pillar_idx:
                    continue
                
                source = pages[idx]
                source_url = source.get("url", "")
                source_content = source.get("content", "")
                
                # Skip utility pages and self-links
                if is_utility_page(source_url, source.get("title", "")):
                    continue
                
                if source_url == pillar_url:
                    continue
                
                # Avoid duplicate links (max 1 per source per topic)
                if source_url not in source_to_target:
                    source_to_target[source_url] = set()
                
                if pillar_url in source_to_target[source_url]:
                    logger.debug(f"Link {source_url} → {pillar_url} already recommended")
                    continue
                
                # Extract anchor text
                phrases = extract_noun_phrases(source_content)
                anchor = select_best_anchor(phrases, pillar_content)
                
                if anchor:
                    source_to_target[source_url].add(pillar_url)
                    rec = LinkRecommendation(
                        source_url=source_url,
                        target_url=pillar_url,
                        anchor=anchor,
                        semantic_score=float(silhouette_score)
                    )
                    recommendations.append(rec.to_dict())
                    logger.info(f"Recommended link: {source_url} → {pillar_url}")
        
        logger.info(f"Generated {len(recommendations)} link recommendations")
        return recommendations
        
    except LinkPlanningError:
        raise
    except Exception as e:
        raise LinkPlanningError(f"Link planning failed: {str(e)}")
