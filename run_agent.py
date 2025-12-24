"""
Main orchestration pipeline for SEO internal linking recommendation agent.
Production-grade with logging, error handling, and n8n integration.
"""

import json
import logging
import logging.handlers
import argparse
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from config import config
from crawler_v2 import crawl_pages, CrawlerError, CrawlResult
from content_extractor_v2 import extract_content, ContentExtractionError
from semantic_topics_v2 import SemanticClusterer, ClusteringError
from internal_link_planner_v2 import plan_semantic_links, LinkPlanningError
from output_writer_v2 import write_csv
from pdf_report import generate_pdf_report

# Configure logging
def setup_logging() -> logging.Logger:
    """
    Configure logging for the application.
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, config.logging.level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.logging.level))
    console_formatter = logging.Formatter(config.logging.format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if config.logging.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            config.logging.log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class AgentResult:
    """Container for agent execution results."""
    
    def __init__(self):
        self.site: str = ""
        self.total_pages: int = 0
        self.usable_pages: int = 0
        self.recommendations: List[Dict[str, Any]] = []
        self.silhouette_score: float = 0.0
        self.execution_time: float = 0.0
        self.errors: List[str] = []
        self.success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "site": self.site,
            "total_pages": self.total_pages,
            "usable_pages": self.usable_pages,
            "recommendations_count": len(self.recommendations),
            "recommendations": self.recommendations,
            "quality_score": f"{self.silhouette_score:.3f}",
            "execution_time_seconds": f"{self.execution_time:.2f}",
            "errors": self.errors,
            "success": self.success,
            "timestamp": datetime.now().isoformat()
        }
    
    def to_json(self) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


def validate_input(site: str) -> None:
    """
    Validate input site URL.
    
    Args:
        site: Site URL to validate
        
    Raises:
        AgentError: If validation fails
    """
    if not site or not isinstance(site, str):
        raise AgentError("Site URL must be a non-empty string")
    
    if not site.startswith(("http://", "https://")):
        raise AgentError("Site URL must start with http:// or https://")
    
    logger.info(f"Input validation passed for: {site}")


def run(
    site: str,
    output_pdf: bool = True,
    output_csv: bool = True,
    output_json: bool = True,
    n8n_mode: bool = False
) -> AgentResult:
    """
    Execute the complete internal linking analysis pipeline.
    
    Args:
        site: Website URL to analyze
        output_pdf: Generate PDF report
        output_csv: Generate CSV output
        output_json: Generate JSON metadata
        n8n_mode: Return JSON for n8n integration
        
    Returns:
        AgentResult with recommendations and metadata
        
    Raises:
        AgentError: If critical pipeline step fails
    """
    result = AgentResult()
    result.site = site
    start_time = datetime.now()
    
    try:
        # Validate input
        logger.info("=== Starting SEO Internal Linking Analysis ===")
        validate_input(site)
        
        # Step 1: Crawl website
        logger.info("Step 1: Crawling website...")
        try:
            crawl_result = crawl_pages(site)
            result.total_pages = crawl_result.total_success
            
            if result.total_pages < 2:
                raise AgentError(
                    f"Crawled only {result.total_pages} pages (need minimum 2)"
                )
            
            logger.info(f"Crawled {result.total_pages} pages successfully")
            
        except CrawlerError as e:
            raise AgentError(f"Crawling failed: {str(e)}")
        
        # Step 2: Extract content
        logger.info("Step 2: Extracting content from pages...")
        pages_data: List[Dict[str, str]] = []
        
        try:
            for page in crawl_result.pages:
                try:
                    content = extract_content(page["html"])
                    page["content"] = content
                    pages_data.append(page)
                    result.usable_pages += 1
                    
                except ContentExtractionError as e:
                    logger.warning(f"Failed to extract from {page.get('url')}: {e}")
                    result.errors.append(str(e))
                    continue
            
            if result.usable_pages < 2:
                raise AgentError(
                    f"Only {result.usable_pages} usable pages (need minimum 2)"
                )
            
            logger.info(f"Extracted content from {result.usable_pages} pages")
            
        except AgentError:
            raise
        except Exception as e:
            raise AgentError(f"Content extraction failed: {str(e)}")
        
        # Step 3: Semantic clustering
        logger.info("Step 3: Performing semantic clustering...")
        try:
            clusterer = SemanticClusterer()
            contents = [p["content"] for p in pages_data]
            
            cluster_labels, silhouette_score = clusterer.cluster_pages(contents)
            result.silhouette_score = silhouette_score
            
            logger.info(
                f"Clustering complete: {len(set(cluster_labels))} clusters, "
                f"silhouette_score={silhouette_score:.3f}"
            )
            
        except ClusteringError as e:
            raise AgentError(f"Clustering failed: {str(e)}")
        except Exception as e:
            raise AgentError(f"Unexpected error in clustering: {str(e)}")
        
        # Step 4: Link planning
        logger.info("Step 4: Planning internal links...")
        try:
            recommendations = plan_semantic_links(
                pages_data,
                cluster_labels,
                silhouette_score
            )
            result.recommendations = recommendations
            
            logger.info(f"Generated {len(recommendations)} link recommendations")
            
        except LinkPlanningError as e:
            raise AgentError(f"Link planning failed: {str(e)}")
        except Exception as e:
            raise AgentError(f"Unexpected error in link planning: {str(e)}")
        
        # Step 5: Output generation
        logger.info("Step 5: Generating outputs...")
        
        try:
            timestamp = datetime.now().strftime(config.output.csv_filename_pattern.split("_")[-2:][0])
            domain = site.split("//")[1].split("/")[0]
            
            # CSV output
            if output_csv and result.recommendations:
                csv_filename = config.output.csv_filename_pattern.format(
                    domain=domain,
                    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                )
                write_csv(result.recommendations, csv_filename)
                logger.info(f"CSV output: {csv_filename}")
            
            # PDF output
            if output_pdf and result.recommendations:
                pdf_filename = config.output.pdf_filename_pattern.format(
                    domain=domain,
                    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                )
                generate_pdf_report(
                    domain=domain,
                    recommendations=result.recommendations,
                    silhouette_score=result.silhouette_score,
                    output_path=pdf_filename
                )
                logger.info(f"PDF output: {pdf_filename}")
            
            # JSON output
            if output_json:
                json_filename = config.output.json_filename_pattern.format(
                    domain=domain,
                    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                )
                with open(json_filename, "w") as f:
                    f.write(result.to_json())
                logger.info(f"JSON output: {json_filename}")
        
        except Exception as e:
            logger.warning(f"Output generation failed: {e}")
            result.errors.append(f"Output generation error: {str(e)}")
        
        # Mark as successful
        result.success = True
        
        # Calculate execution time
        result.execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info("=== Analysis Complete ===")
        logger.info(f"Total execution time: {result.execution_time:.2f} seconds")
        
        return result
        
    except AgentError as e:
        logger.error(f"Agent error: {str(e)}")
        result.errors.append(str(e))
        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result
    
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")
        result.errors.append(f"Unexpected error: {str(e)}")
        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result


def main() -> int:
    """
    Main entry point with CLI argument handling.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="SEO Internal Linking Recommendation Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py --site https://example.com
  python run_agent.py --site https://example.com --no-pdf --json-only
  python run_agent.py --site https://example.com --n8n-mode
        """
    )
    
    parser.add_argument(
        "--site",
        type=str,
        required=True,
        help="Website URL to analyze (required)"
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF report generation"
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip CSV output generation"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Generate only JSON output (skip PDF and CSV)"
    )
    parser.add_argument(
        "--n8n-mode",
        action="store_true",
        help="Output JSON for n8n integration"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Adjust logging if debug mode
    if args.debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Determine output options
    output_pdf = not args.no_pdf and not args.json_only
    output_csv = not args.no_csv and not args.json_only
    output_json = True  # Always output JSON for n8n compatibility
    
    try:
        result = run(
            site=args.site,
            output_pdf=output_pdf,
            output_csv=output_csv,
            output_json=output_json,
            n8n_mode=args.n8n_mode
        )
        
        # Output result
        if args.n8n_mode:
            print(result.to_json())
        else:
            print(f"\nAnalysis Summary:")
            print(f"  Site: {result.site}")
            print(f"  Pages crawled: {result.total_pages}")
            print(f"  Pages analyzed: {result.usable_pages}")
            print(f"  Recommendations: {len(result.recommendations)}")
            print(f"  Quality score: {result.silhouette_score:.3f}")
            print(f"  Execution time: {result.execution_time:.2f}s")
        
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 1
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())

