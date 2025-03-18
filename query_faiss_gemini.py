import os
import faiss
import numpy as np
import pickle
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import requests

# 🔹 Load embedding model
embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")

# 🔹 FAISS Index Paths
vector_store_path = "vector_store"
faiss_index_path = os.path.join(vector_store_path, "index.faiss")
metadata_path = os.path.join(vector_store_path, "metadata.pkl")

# 🔹 Load FAISS Index
if os.path.exists(faiss_index_path):
    index = faiss.read_index(faiss_index_path)
    print("🔄 Loaded FAISS index.")
else:
    raise FileNotFoundError("❌ FAISS index not found! Run `store_faiss.py` first.")

# 🔹 Load Metadata
if os.path.exists(metadata_path):
    with open(metadata_path, "rb") as f:
        chunk_metadata = pickle.load(f)
    print(f"🔄 Loaded metadata ({len(chunk_metadata)} chunks).")
else:
    raise FileNotFoundError("❌ Metadata not found! Run `store_faiss.py` first.")

# 🔹 BM25 Index for Keyword Search
bm25_corpus = [chunk_metadata[i] for i in range(len(chunk_metadata))]
bm25_tokenized = [chunk.split() for chunk in bm25_corpus]
bm25 = BM25Okapi(bm25_tokenized)

# 🔹 Configure Gemini API
genai.configure(api_key="AIzaSyCNOT1X_kRDcsx6UOZFCWNAUqFao4ffK-4")
gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Change model if needed

def google_search(query):
    """Search Google for additional information."""
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key=YOUR_GOOGLE_API_KEY&cx=YOUR_CUSTOM_SEARCH_ENGINE_ID"
    try:
        response = requests.get(search_url)
        data = response.json()
        search_results = [item["snippet"] for item in data.get("items", [])[:3]]  # Top 3 results
        return "\n".join(search_results)
    except Exception as e:
        return f"Google search failed: {str(e)}"

def query_faiss_bm25(question, top_k=15):  # Increase to 15 chunks
    """Retrieve top-k chunks using FAISS and BM25 hybrid search with keyword filtering."""
    
    question_embedding = embedding_model.encode([question]).astype('float32')
    faiss.normalize_L2(question_embedding)  
    D, I = index.search(question_embedding, top_k)

    faiss_chunks = [chunk_metadata[idx] for idx in I[0] if idx in chunk_metadata]
    bm25_results = bm25.get_top_n(question.split(), bm25_corpus, n=top_k)

    retrieved_chunks = list(set(bm25_results + faiss_chunks))

    # 🔹 Only keep chunks that explicitly mention VAT
    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if "VAT" in chunk or "visual assessment of tendency" in chunk.lower()
    ]

    # 🔹 If no relevant chunks found, use all retrieved chunks
    if not relevant_chunks:
        relevant_chunks = retrieved_chunks

    # 🔹 Increase number of chunks sent to Gemini
    relevant_chunks = relevant_chunks[:8]  # Send top 8 instead of 5

    # 🔹 DEBUG: Print retrieved chunks after filtering
    print("\n📌 DEBUG: Retrieved Chunks from FAISS (Expanded & Filtered for VAT):\n")
    for i, chunk in enumerate(relevant_chunks):
        print(f"{i+1}. {chunk[:300]}...")  # Print first 300 characters

    return relevant_chunks
def generate_gemini_answer(question, retrieved_chunks, use_google=False, use_db=False):
    """Generate an AI answer using Gemini API based on FAISS chunks + optional Google Search + DB."""

    # 🔹 Ensure all chunks are valid strings
    retrieved_chunks = [str(chunk).strip() for chunk in retrieved_chunks if isinstance(chunk, str) and len(chunk.strip()) > 10]

    # 🔹 If no valid chunks, return an error message
    if not retrieved_chunks:
        return "⚠️ No relevant information found in the research papers."

    # 🔹 Step 1: Summarize Retrieved Chunks
    summarization_prompt = f"""
    You are an expert research assistant. Your task is to summarize the following research paper extracts into a short, clear, and informative paragraph.
    
    📚 **Extracts from the research paper:**  
    {"\n\n---\n\n".join(retrieved_chunks[:8])}

    🎯 **Summarized Key Information (Make it clear & precise):**
    """

    print("\n📌 DEBUG: Sending Summarization Request to Gemini\n", summarization_prompt[:1500])  # Debugging output

    summary_response = gemini_model.generate_content(summarization_prompt)
    summarized_chunks = summary_response.text if summary_response else "❌ Summarization failed."

    # 🔹 Step 2: Use the Summarized Content to Answer the Question
    prompt = f"""
    You are an AI assistant specializing in research-based answers.
    **Your only source of knowledge is the summarized research paper data.**
    
    🚨 **STRICT RULE:** Your response must be based on the provided summarized research paper data.

    🔍 **Question:** {question}
    
    📚 **Summarized Research Paper Data:**  
    {summarized_chunks}

    ✅ **If full details are not available, answer based on partial information.**
    🚫 **DO NOT say "No relevant information found." Instead, summarize what is available.**
    """

    print("\n📌 DEBUG: Sent Final Query to Gemini API (Fixed Input)\n", prompt[:1500])  # Debugging output

    response = gemini_model.generate_content(prompt)
    return response.text if response else "❌ Gemini API failed."

# 🔹 RUN SCRIPT
if __name__ == "__main__":
    while True:
        user_query = input("\n🔍 Enter your question (or type 'exit' to stop): ")
        if user_query.lower() == "exit":
            break

        # 🔹 Retrieve chunks
        top_chunks = query_faiss_bm25(user_query)

        # 🔹 Ask user if they want Google Search & Database lookup
        use_google = input("🌐 Include Google Search? (y/n): ").strip().lower() == "y"
        use_db = input("📂 Include Custom Database? (y/n): ").strip().lower() == "y"

        # 🔹 Get AI answer
        ai_answer = generate_gemini_answer(user_query, "\n".join(top_chunks), use_google, use_db)

        print("\n🤖 **AI-Generated Answer:**\n")
        print(ai_answer)
        print("=" * 100)
