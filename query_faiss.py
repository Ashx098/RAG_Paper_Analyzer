import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# 🔹 Load a better embedding model for retrieval
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

# 🔹 Normalize FAISS to Use Cosine Similarity
faiss.normalize_L2(index.reconstruct_n(0, index.ntotal))  # Normalize stored embeddings

def query_faiss(question, top_k=10):
    """Retrieves top-k most relevant chunks from FAISS using cosine similarity."""
    # Convert query into embedding
    question_embedding = embedding_model.encode([question]).astype('float32')

    # Normalize query embedding for cosine similarity
    faiss.normalize_L2(question_embedding)  

    # Perform similarity search in FAISS
    D, I = index.search(question_embedding, top_k)  # D = distances, I = indices

    retrieved_chunks = []
    for idx in I[0]:
        if idx in chunk_metadata:
            retrieved_chunks.append(chunk_metadata[idx])

    return retrieved_chunks

# 🔹 RUN SCRIPT
if __name__ == "__main__":
    while True:
        user_query = input("\n🔍 Enter your question (or type 'exit' to stop): ")
        if user_query.lower() == "exit":
            break

        top_chunks = query_faiss(user_query)

        print("\n📌 Top Matching Chunks:\n")
        for i, chunk in enumerate(top_chunks):
            print(f"{i+1}. {chunk[:500]}...\n")  # Show first 500 characters
            print("=" * 80)
