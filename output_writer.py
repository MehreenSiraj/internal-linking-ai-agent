import pandas as pd

def write_csv(links, output_file="internal_linking_plan.csv"):
    """
    Write links to CSV with deduplication.
    
    Args:
        links: List of link dicts
        output_file: Output filename (default: internal_linking_plan.csv)
    
    Returns:
        Path to written file
    """
    df = pd.DataFrame(links)
    df.drop_duplicates(inplace=True)
    df.to_csv(output_file, index=False)
    return output_file
