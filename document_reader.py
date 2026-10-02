import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any

class DocumentReaderError(Exception):
    """Custom exception for document reading errors."""
    pass

def read_pdf(file_path: Path) -> Dict[str, Any]:
    """
    Validates and extracts text from a PDF file page by page.
    
    Args:
        file_path (Path): Path to the PDF file.
        
    Returns:
        dict: A dictionary containing the filename, page count, and page text.
    """
    if not file_path.exists():
        raise DocumentReaderError(f"File not found: {file_path}")
        
    if file_path.suffix.lower() != ".pdf":
        raise DocumentReaderError(f"File is not a PDF: {file_path}")

    doc_data = {
        "filename": file_path.name,
        "page_count": 0,
        "pages": []
    }

    try:
        # Open the document safely
        with fitz.open(file_path) as pdf_document:
            doc_data["page_count"] = len(pdf_document)
            
            if doc_data["page_count"] == 0:
                raise DocumentReaderError("The PDF document is completely empty (0 pages).")
                
            for page_num in range(doc_data["page_count"]):
                page = pdf_document.load_page(page_num)
                text = page.get_text("text").strip()
                
                doc_data["pages"].append({
                    "page_number": page_num + 1,  # 1-indexed for human readability
                    "text": text if text else "[NO EXTRACTABLE TEXT ON THIS PAGE]"
                })
                
    except fitz.FileDataError as e:
        raise DocumentReaderError(f"The PDF file is corrupted or unreadable: {str(e)}")
    except Exception as e:
        raise DocumentReaderError(f"An unexpected error occurred while reading the PDF: {str(e)}")

    # Check if we extracted any actual text at all
    all_text = "".join([p["text"] for p in doc_data["pages"]])
    if not all_text.replace("[NO EXTRACTABLE TEXT ON THIS PAGE]", "").strip():
        raise DocumentReaderError("The PDF contains no extractable text. It might be a scanned image without OCR.")

    return doc_data