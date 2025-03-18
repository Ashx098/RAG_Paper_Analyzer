# 📄 RAG Paper Analyzer

### **🚀 A Retrieval-Augmented Generation (RAG) system to analyze research papers efficiently.**

## **📌 Features**
✅ Extracts text from PDFs using **`pdfplumber`**, **`PyMuPDF`**, and **OCR (Tesseract)**  
✅ Splits text into **structured chunks** for efficient retrieval  
✅ Uses **FAISS (Vector Search) + Sentence Transformers** for similarity search  
✅ Queries research paper data using **GPT-4/Gemini AI** (RAG)  
✅ Supports **Hybrid Retrieval** (Google Search + Custom Database)  

## **📂 Project Structure**
RAG_Paper_Analyzer ├── 📂 pdfs # Raw research papers (PDF format) ├── 📂 extracted_text # Extracted text files ├── 📂 chunked_text # Chunked data for FAISS ├── 📂 vector_store # FAISS vector index storage ├── extract_text.py # Extracts text from PDFs ├── chunk_text.py # Splits text into meaningful chunks ├── store_faiss.py # Stores chunks in FAISS for retrieval ├── query_faiss.py # Searches FAISS for relevant research chunks ├── query_faiss_gemini.py # Uses Gemini API to generate responses from FAISS ├── requirements.txt # Python dependencies ├── .gitignore # Excluded files for Git └── README.md # Documentation

## **🛠️ To-Do List **
 Improve LLM response generation (Replace Gemini with GPT-4/Claude)
 Add Google Search API integration for external retrieval
 Implement Custom Database Retrieval
