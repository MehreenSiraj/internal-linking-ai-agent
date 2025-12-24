"""
Output writing utilities for CSV and data export.
Production-grade with error handling and validation.
"""

import logging
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class OutputError(Exception):
    """Raised when output generation fails."""
    pass


def validate_recommendations(
    recommendations: List[Dict[str, Any]]
) -> None:
    """
    Validate recommendation list structure.
    
    Args:
        recommendations: List of recommendation dicts
        
    Raises:
        OutputError: If validation fails
    """
    if not isinstance(recommendations, list):
        raise OutputError("Recommendations must be a list")
    
    required_fields = {"source_url", "target_url", "anchor"}
    
    for idx, rec in enumerate(recommendations):
        if not isinstance(rec, dict):
            raise OutputError(f"Recommendation {idx} is not a dictionary")
        
        missing = required_fields - set(rec.keys())
        if missing:
            raise OutputError(
                f"Recommendation {idx} missing fields: {missing}"
            )


def write_csv(
    recommendations: List[Dict[str, Any]],
    filename: str,
    deduplicate: bool = True
) -> str:
    """
    Write recommendations to CSV file.
    
    Args:
        recommendations: List of recommendation dicts
        filename: Output CSV filename
        deduplicate: Remove duplicate links before writing
        
    Returns:
        Path to written file
        
    Raises:
        OutputError: If writing fails
    """
    try:
        validate_recommendations(recommendations)
        
        # Deduplicate if requested
        if deduplicate:
            seen = set()
            unique = []
            for rec in recommendations:
                key = (rec.get("source_url"), rec.get("target_url"))
                if key not in seen:
                    seen.add(key)
                    unique.append(rec)
            recommendations = unique
            logger.debug(f"Deduplicated to {len(recommendations)} unique links")
        
        # Ensure output directory exists
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write CSV
        fieldnames = ["source_url", "target_url", "anchor", "semantic_score"]
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for rec in recommendations:
                row = {
                    "source_url": rec.get("source_url", ""),
                    "target_url": rec.get("target_url", ""),
                    "anchor": rec.get("anchor", ""),
                    "semantic_score": rec.get("semantic_score", "")
                }
                writer.writerow(row)
        
        logger.info(f"Wrote {len(recommendations)} recommendations to {filename}")
        return str(output_path)
        
    except OutputError:
        raise
    except Exception as e:
        raise OutputError(f"CSV writing failed: {str(e)}")


def write_json(
    data: Dict[str, Any],
    filename: str
) -> str:
    """
    Write data to JSON file.
    
    Args:
        data: Data dictionary to write
        filename: Output JSON filename
        
    Returns:
        Path to written file
        
    Raises:
        OutputError: If writing fails
    """
    try:
        import json
        
        # Ensure output directory exists
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Wrote data to {filename}")
        return str(output_path)
        
    except Exception as e:
        raise OutputError(f"JSON writing failed: {str(e)}")
