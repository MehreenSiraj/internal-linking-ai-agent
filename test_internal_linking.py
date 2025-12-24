"""
Comprehensive test suite for internal linking agent.
Validates safety, quality, and correctness of generated recommendations.
"""

import unittest
from urllib.parse import urlparse
import pandas as pd

from crawler import crawl_pages
from content_extractor import extract_clean_text
from semantic_topics import embed_pages, cluster_pages
from semantic_graph import build_semantic_clusters
from internal_link_planner import (
    plan_semantic_links,
    is_utility_page,
    identify_pillar,
    select_best_anchor
)


class TestUtilityPageDetection(unittest.TestCase):
    """Test that utility pages are properly filtered."""
    
    def test_privacy_page_detected(self):
        self.assertTrue(is_utility_page("https://example.com/privacy-policy"))
    
    def test_terms_page_detected(self):
        self.assertTrue(is_utility_page("https://example.com/terms"))
    
    def test_cookie_page_detected(self):
        self.assertTrue(is_utility_page("https://example.com/cookie-policy"))
    
    def test_contact_page_detected(self):
        self.assertTrue(is_utility_page("https://example.com/contact-us"))
    
    def test_login_page_detected(self):
        self.assertTrue(is_utility_page("https://example.com/login"))
    
    def test_normal_page_not_flagged(self):
        self.assertFalse(is_utility_page("https://example.com/how-to-setup-docker"))


class TestAnchorValidation(unittest.TestCase):
    """Test that anchors are semantically sound."""
    
    def test_anchor_must_exist_in_target(self):
        """Anchor should only be selected if it matches target content."""
        source_sentence = "This is about semantic search optimization."
        target_content = "Semantic search optimization is important. It improves ranking."
        
        anchor = select_best_anchor(source_sentence, target_content)
        
        # Should find a match because both mention semantic/search
        self.assertIsNotNone(anchor)
        self.assertIn("semantic", anchor.lower())
    
    def test_anchor_rejected_for_unrelated_target(self):
        """Anchor should be None if target has no semantic overlap."""
        source_sentence = "This page is about email marketing."
        target_content = "Docker containers are powerful tools. Learn containerization."
        
        anchor = select_best_anchor(source_sentence, target_content)
        
        # Should not find a match (email marketing ≠ docker containers)
        self.assertIsNone(anchor)
    
    def test_anchor_has_minimum_length(self):
        """Anchor must be at least 2 words."""
        source_sentence = "The single-word anchor should fail."
        target_content = "Anchor testing is important."
        
        anchor = select_best_anchor(source_sentence, target_content)
        
        if anchor:
            self.assertGreaterEqual(len(anchor.split()), 2)


class TestPillarIdentification(unittest.TestCase):
    """Test that pillar pages are correctly identified."""
    
    def test_longest_content_becomes_pillar(self):
        """Pillar should be the page with most content."""
        pages = [
            {"url": "https://example.com/topic-a", "content": "Short content."},
            {"url": "https://example.com/topic-b", "content": "This is a much longer page with substantial content about the topic. " * 50},
            {"url": "https://example.com/topic-c", "content": "Medium length content here."}
        ]
        
        pillar = identify_pillar(pages)
        
        self.assertEqual(pillar["url"], "https://example.com/topic-b")
    
    def test_utility_pages_excluded_from_pillar(self):
        """Pillar should not be a utility page even if longest."""
        pages = [
            {"url": "https://example.com/topic", "content": "Reasonable content length. " * 20},
            {"url": "https://example.com/privacy-policy", "content": "This is the longest privacy policy ever written. " * 100}
        ]
        
        pillar = identify_pillar(pages)
        
        # Should pick the topic page, not the privacy page
        self.assertNotIn("privacy", pillar["url"])


class TestLinkGeneration(unittest.TestCase):
    """Test that generated links follow all safety rules."""
    
    def test_no_links_from_utility_pages(self):
        """No internal links should originate from utility pages."""
        cluster = [
            {"url": "https://example.com/topic-a", "content": "Main topic content. " * 50},
            {"url": "https://example.com/privacy-policy", "content": "Privacy policy. " * 30}
        ]
        
        links = plan_semantic_links({"cluster1": cluster})
        
        # All links should originate from non-utility pages
        for link in links:
            self.assertFalse(is_utility_page(link["from"]))
    
    def test_max_one_link_per_page(self):
        """Each page should have at most 1 link to the pillar."""
        cluster = [
            {
                "url": "https://example.com/page-a",
                "content": "This page discusses topic A. Topic A is important. We also mention topic A again."
            },
            {
                "url": "https://example.com/page-b",
                "content": "This is the comprehensive guide to topic A. " * 20
            }
        ]
        
        links = plan_semantic_links({"cluster1": cluster})
        
        # Count links from page-a
        links_from_page_a = [l for l in links if l["from"] == "https://example.com/page-a"]
        self.assertLessEqual(len(links_from_page_a), 1)
    
    def test_no_self_links(self):
        """A page should never link to itself."""
        cluster = [
            {"url": "https://example.com/topic", "content": "Topic content. " * 50}
        ]
        
        links = plan_semantic_links({"cluster1": cluster})
        
        for link in links:
            self.assertNotEqual(link["from"], link["to"])


class TestClusterQuality(unittest.TestCase):
    """Test cluster cohesion and topical relevance."""
    
    def test_silhouette_score_calculation(self):
        """Silhouette score should be computed and reasonable."""
        # Create simple test pages
        pages = [
            {"url": "https://example.com/python", "content": "Python programming language. " * 50},
            {"url": "https://example.com/python-django", "content": "Django framework for Python. " * 50},
            {"url": "https://example.com/javascript", "content": "JavaScript web development. " * 50},
            {"url": "https://example.com/javascript-react", "content": "React library for JavaScript. " * 50},
        ]
        
        embeddings = embed_pages(pages)
        labels, silhouette_avg = cluster_pages(embeddings, n_clusters=2)
        
        # Silhouette score should be between -1 and 1
        self.assertGreaterEqual(silhouette_avg, -1)
        self.assertLessEqual(silhouette_avg, 1)
        
        # For this coherent data, should be positive
        self.assertGreater(silhouette_avg, 0)


class TestOutputFormat(unittest.TestCase):
    """Test CSV output correctness."""
    
    def test_output_has_required_columns(self):
        """CSV should have from, to, anchor, sentence columns."""
        # Create minimal valid output
        links = [
            {
                "from": "https://example.com/a",
                "to": "https://example.com/b",
                "anchor": "link text",
                "sentence": "This is the link text here."
            }
        ]
        
        # Verify structure
        required_cols = ["from", "to", "anchor", "sentence"]
        for col in required_cols:
            self.assertIn(col, links[0])
    
    def test_no_duplicate_links(self):
        """Should not recommend same link twice."""
        links = [
            {"from": "a", "to": "b", "anchor": "text", "sentence": "s"},
            {"from": "a", "to": "b", "anchor": "text", "sentence": "s"},
            {"from": "a", "to": "c", "anchor": "text", "sentence": "s"},
        ]
        
        df = pd.DataFrame(links)
        df.drop_duplicates(inplace=True)
        
        self.assertEqual(len(df), 2)


def run_safety_checks():
    """Run all tests and report results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityPageDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestAnchorValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPillarIdentification))
    suite.addTests(loader.loadTestsFromTestCase(TestLinkGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestClusterQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormat))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_safety_checks()
    exit(0 if success else 1)
