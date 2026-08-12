import os
from typing import Tuple, Dict, Any

class DocumentValidator:
    @staticmethod
    def validate_pdf(pdf_path: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate the generated PDF.
        For MVP, we just check if it exists and has a minimum size.
        In a real implementation, we could use PyPDF2 or pdfminer to extract text 
        and verify that the required variables (client_name, total_ttc, etc) are present.
        """
        if not os.path.exists(pdf_path):
            return False, "PDF file does not exist."
            
        file_size = os.path.getsize(pdf_path)
        if file_size < 1024:  # Minimum 1KB to consider it valid
            return False, f"PDF file is too small ({file_size} bytes), likely corrupted or empty."
            
        # Basic validation passes
        return True, ""
