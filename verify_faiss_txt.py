import os

def analyze_text_chunks(folder_path):
    """Reads text chunk files and checks quality before FAISS storage."""
    txt_files = [f for f in os.listdir(folder_path) if f.endswith("_chunks.txt")]

    if not txt_files:
        print("⚠️ No chunked text files found in the folder.")
        return

    print("\n🔍 Analyzing Chunk Quality...\n")

    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)

        print(f"📄 Verifying: {filename}")
        print("=" * 80)

        with open(file_path, "r", encoding="utf-8") as file:
            chunks = file.read().split("\n\n---\n\n")  # Split chunks based on separator

        for i, chunk in enumerate(chunks):
            print(f"\n🔹 Chunk {i+1}:")
            print(chunk[:500])  # Display first 500 characters
            print("-" * 60)

            # Check for issues
            if len(chunk) < 100:
                print("⚠️ Warning: Chunk is too short, might be incomplete.")
            if "figure" in chunk.lower() or "table" in chunk.lower():
                print("⚠️ Warning: Chunk contains references to figures/tables.")
            if chunk.count(".") < 2:  # If chunk has fewer than 2 sentences
                print("⚠️ Warning: Possible incomplete chunk (too few sentences).")

        print("=" * 80)

# 🔹 RUN SCRIPT
if __name__ == "__main__":
    chunked_text_folder = "D:\\RAG_Paper_Analyzer\\chunked_text"
    analyze_text_chunks(chunked_text_folder)
