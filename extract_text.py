import fitz  # PyMuPDF (best for structured PDFs)
import pdfplumber
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import re
import os

# 🔹 TEXT CLEANING FUNCTION
def clean_text(text):
    """Cleans extracted text: removes citations, metadata, extra spaces, and numbers-only lines."""
    cleaned_lines = []
    for line in text.split("\n"):
        line = line.strip()

        # Remove funding acknowledgments, metadata, and unnecessary headers
        if any(kw in line.lower() for kw in ["research supported", "funded by", "grant", "see profile", "figure", "table", "abstract"]):
            continue  # Skip unwanted lines

        # Remove citation references like [9], [16]
        line = re.sub(r'\[\d+\]', '', line)

        # Remove excessive spaces & numbers-only lines
        if not re.match(r'^\s*[\d\s\W]+\s*$', line):
            cleaned_lines.append(re.sub(r'\s+', ' ', line))  # Remove extra spaces

    return "\n".join(cleaned_lines).strip()

# 🔹 PDF EXTRACTION METHODS
def extract_text_pymupdf(pdf_path):
    """Extracts text using PyMuPDF (best for structured PDFs)."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"❌ PyMuPDF failed: {e}")
    return clean_text(text)

def extract_text_pdfplumber(pdf_path):
    """Extracts text using PDFPlumber (good for multi-column PDFs)."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"❌ PDFPlumber failed: {e}")
    return clean_text(text)

def extract_text_pypdf2(pdf_path):
    """Extracts text using PyPDF2 (fallback method)."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
    except Exception as e:
        print(f"❌ PyPDF2 failed: {e}")
    return clean_text(text)

def extract_text_ocr(pdf_path):
    """Extracts text using OCR for scanned PDFs."""
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    except Exception as e:
        print(f"❌ OCR failed: {e}")
    return clean_text(text)

def extract_text_from_pdf(pdf_path):
    """Hybrid text extraction: PyMuPDF → PDFPlumber → PyPDF2 → OCR"""
    text = extract_text_pymupdf(pdf_path)

    if len(text) < 500:  # If text is too short, try PDFPlumber
        print("⚠️ Fallback to PDFPlumber...")
        text = extract_text_pdfplumber(pdf_path)

    if len(text) < 500:  # If still not enough text, use PyPDF2
        print("⚠️ Fallback to PyPDF2...")
        text = extract_text_pypdf2(pdf_path)

    if len(text) < 500:  # If still no good text, use OCR
        print("⚠️ Fallback to OCR...")
        text = extract_text_ocr(pdf_path)

    return text if text else "⚠️ Text extraction failed."

# 🔹 MAIN PROCESS FUNCTION
def process_pdfs(folder_path, output_folder="extracted_text"):
    """Processes all PDFs in a folder and extracts clean text."""
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("⚠️ No PDF files found in the folder.")
        return
    
    os.makedirs(output_folder, exist_ok=True)  # Create output folder if not exists

    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        print(f"\n📄 Processing: {filename}...")

        extracted_text = extract_text_from_pdf(pdf_path)

        if extracted_text:
            output_file = os.path.join(output_folder, f"{filename}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            print(f"✅ Extracted text saved to: {output_file}")
            print("=" * 80)

# 🔹 RUN SCRIPT
if __name__ == "__main__":
    pdf_folder = "D:\\RAG_Paper_Analyzer\\pdfs"  # Update with your folder path
    process_pdfs(pdf_folder)
