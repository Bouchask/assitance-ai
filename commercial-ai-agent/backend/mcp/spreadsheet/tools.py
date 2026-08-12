import pandas as pd
import os
from typing import List, Dict, Any

def search_spreadsheet(filepath: str, query_column: str, query_value: str) -> List[Dict[str, Any]]:
    """Search an Excel or CSV file for rows matching a query."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_root = os.path.realpath(os.path.join(project_root, "data"))
        resolved_path = os.path.realpath(filepath)
        if os.path.commonpath([data_root, resolved_path]) != data_root:
            raise ValueError("Spreadsheet must be located in the managed data directory.")
        if not os.path.isfile(resolved_path):
            raise FileNotFoundError("Spreadsheet file not found.")
        if resolved_path.endswith('.csv'):
            df = pd.read_csv(resolved_path)
        elif resolved_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(resolved_path)
        else:
            raise ValueError("Unsupported file format. Use .csv, .xls, or .xlsx")
            
        if query_column not in df.columns:
            raise ValueError(f"Column '{query_column}' not found in spreadsheet.")
            
        # Convert everything to string for loose matching, or exact match if needed
        # We do a simple exact match for this basic tool
        # In a real app we'd normalize the data schema
        matched_df = df[df[query_column].astype(str) == str(query_value)]
        
        # Replace NaN with None for JSON serialization
        matched_df = matched_df.where(pd.notnull(matched_df), None)
        return matched_df.to_dict(orient='records')
        
    except Exception as e:
        raise RuntimeError(f"Failed to search spreadsheet: {str(e)}")
