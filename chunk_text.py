import os
import re
import hashlib
import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize

class ResearchPaperProcessor:
    """Robust PDF processor with error handling"""
    
    def __init__(self):
        self.min_chunk_length = 500
        self.max_chunk_size = 1200
        self.section_headers = [
            'abstract', 'introduction', 'methodology', 
            'results', 'conclusion', 'references'
        ]
        
    def extract_text(self, pdf_path: str) -> str:
        """Safe PDF text extraction with error handling"""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    blocks = page.get_text("blocks")
                    prev_block = (0, 0, 0, 0, "")  # Initialize with empty text
                    
                    for block in blocks:
                        if len(block) < 5:  # Skip invalid blocks
                            continue
                            
                        if self._is_header_footer(block, page):
                            continue
                            
                        if self._is_duplicate(block, prev_block):
                            continue
                            
                        text += block[4] + "\n"
                        prev_block = block
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
        return text

    def _is_header_footer(self, block, page) -> bool:
        """Improved header/footer detection"""
        if len(block) < 5:
            return False
        y0 = block[1]
        return y0 < 70 or y0 > page.rect.height - 70  # 70px margins

    def _is_duplicate(self, current, previous) -> bool:
        """Safe duplicate detection"""
        try:
            if len(previous) < 5 or len(current) < 5:
                return False
                
            current_text = current[4].strip()
            prev_text = previous[4].strip()
            
            if not current_text or not prev_text:
                return False
                
            return hashlib.md5(current_text.encode()).hexdigest() == \
                   hashlib.md5(prev_text.encode()).hexdigest()
        except:
            return False

    def chunk_text(self, text: str) -> list:
        """Enhanced chunking with error resilience"""
        if not text:
            return []
            
        try:
            # Preprocessing
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'-\n(\w)', r'\1', text)
            
            # Section-aware splitting
            sections = re.split(
                r'\n\s*(\d+\.\s*.*|{}):?\s*\n'.format('|'.join(self.section_headers)),
                text,
                flags=re.IGNORECASE
            )
            
            chunks = []
            current_chunk = []
            
            for section in filter(None, sections):
                if re.match(r'\d+\.|\b(?:{})\b'.format('|'.join(self.section_headers)), section, re.I):
                    if current_chunk:
                        chunks.append("\n".join(current_chunk))
                        current_chunk = []
                    current_chunk.append(section)
                else:
                    sentences = sent_tokenize(section)
                    for sent in sentences:
                        if sum(len(s) for s in current_chunk) + len(sent) > self.max_chunk_size:
                            chunks.append("\n".join(current_chunk))
                            current_chunk = current_chunk[-2:]  # Minimal overlap
                        current_chunk.append(sent)
            
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                
            return [c.strip() for c in chunks if len(c.strip()) >= self.min_chunk_length]
            
        except Exception as e:
            print(f"Chunking error: {str(e)}")
            return []

def process_papers(input_dir: str, output_dir: str):
    """Main processing function with safety checks"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        processor = ResearchPaperProcessor()
        
        for filename in os.listdir(input_dir):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(input_dir, filename)
                print(f"Processing: {filename}")
                
                text = processor.extract_text(pdf_path)
                chunks = processor.chunk_text(text)
                
                output_path = os.path.join(output_dir, f"{filename}_chunks.txt")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("\n\n---\n\n".join(chunks))
                    
                print(f"Created {len(chunks)} chunks for {filename}")
                
    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    process_papers(
        input_dir="D:\\RAG_Paper_Analyzer\\pdfs",
        output_dir="D:\\RAG_Paper_Analyzer\\chunked_text"
    )