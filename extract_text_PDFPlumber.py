import pdfplumber
import os

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using pdfplumber (better accuracy)."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def process_pdfs(folder_path):
    """Processes all PDFs in the given folder and extracts text."""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            print(f"Extracted text from {filename}:\n")
            print(text[:10000])  # Print first 1000 characters for preview
            print("\n" + "="*80 + "\n")

# Run the script with a sample folder
if __name__ == "__main__":
    pdf_folder = "D:\\RAG_Paper_Analyzer\\pdfs"  # Change this if needed
    os.makedirs(pdf_folder, exist_ok=True)  # Create folder if not exists
    process_pdfs(pdf_folder)