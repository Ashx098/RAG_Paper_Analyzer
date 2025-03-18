import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# 🔹 Use the same embedding model for consistency
embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")
vector_dim = 1024  # Correct dimension for this model

# 🔹 FAISS Index Paths
vector_store_path = "vector_store"
faiss_index_path = os.path.join(vector_store_path, "index.faiss")
metadata_path = os.path.join(vector_store_path, "metadata.pkl")

# 🔹 Ensure the vector_store directory exists
os.makedirs(vector_store_path, exist_ok=True)

# 🔹 Create New FAISS Index
index = faiss.IndexFlatL2(vector_dim)
print("✅ Created new FAISS index.")

chunk_metadata = {}

def store_chunks_in_faiss(folder_path):
    """Encodes and stores text chunks in FAISS."""
    txt_files = [f for f in os.listdir(folder_path) if f.endswith("_chunks.txt")]

    if not txt_files:
        print("⚠️ No chunked text files found.")
        return

    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)
        print(f"\n📄 Processing: {filename}...")

        with open(file_path, "r", encoding="utf-8") as file:
            chunks = file.read().split("\n\n---\n\n")  # Split based on separator

        # Convert chunks to embeddings
        embeddings = embedding_model.encode(chunks, convert_to_tensor=False)
        embeddings_np = np.array(embeddings).astype('float32')  # Convert to NumPy array
        index.add(embeddings_np)  # Add embeddings to FAISS index

        # Store chunk metadata
        start_index = len(chunk_metadata)
        for i, chunk in enumerate(chunks):
            chunk_metadata[start_index + i] = chunk

        print(f"✅ Stored {len(chunks)} chunks in FAISS.")

    # Save FAISS Index & Metadata
    faiss.write_index(index, faiss_index_path)
    with open(metadata_path, "wb") as f:
        pickle.dump(chunk_metadata, f)

    print("💾 FAISS index and metadata saved successfully.")

# 🔹 RUN SCRIPT
if __name__ == "__main__":
    chunked_text_folder = "D:\\RAG_Paper_Analyzer\\chunked_text"
    store_chunks_in_faiss(chunked_text_folder)
