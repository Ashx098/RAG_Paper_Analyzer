import os
import pdfplumber
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better for multi-column PDFs)."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PDFPlumber failed: {e}")
    return text.strip()

def extract_text_pypdf2(pdf_path):
    """Extract text using PyPDF2 (fallback method)."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
    return text.strip()

def extract_text_ocr(pdf_path):
    """Extract text using OCR for scanned PDFs."""
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """Hybrid text extraction: PDFPlumber → PyPDF2 → OCR"""
    text = extract_text_pdfplumber(pdf_path)
    
    # If text is too short, try PyPDF2
    if len(text) < 500:  # Adjust threshold as needed
        print("Fallback to PyPDF2...")
        text = extract_text_pypdf2(pdf_path)
    
    # If still not enough text, use OCR
    if len(text) < 500:
        print("Fallback to OCR...")
        text = extract_text_ocr(pdf_path)

    return text if text else "Text extraction failed."

def process_pdfs(folder_path):
    """Processes all PDFs in the given folder and extracts text."""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            print(f"Extracted text from {filename}:\n")
            print(text[:1000])  # Print first 1000 characters for preview
            print("\n" + "="*80 + "\n")

# Run the script
if __name__ == "__main__":
    pdf_folder = "D:\\RAG_Paper_Analyzer\\pdfs"  # Change this if needed
    os.makedirs(pdf_folder, exist_ok=True)
    process_pdfs(pdf_folder)
