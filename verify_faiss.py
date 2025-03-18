import os
import json

def analyze_json_chunks(folder_path):
    """Reads JSON chunk files and checks quality before FAISS storage."""
    json_files = [f for f in os.listdir(folder_path) if f.endswith("_chunks.json")]

    if not json_files:
        print("⚠️ No chunked JSON files found in the folder.")
        return

    print("\n🔍 Analyzing Chunk Quality...\n")

    for filename in json_files:
        file_path = os.path.join(folder_path, filename)

        print(f"📄 Verifying: {filename}")
        print("=" * 80)

        with open(file_path, "r", encoding="utf-8") as file:
            chunks = json.load(file)  # Directly load as a list

        if not isinstance(chunks, list):  # Ensure it's a list
            print(f"❌ Error: {filename} does not contain a list of chunks!")
            continue

        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get("text", "")

            print(f"\n🔹 Chunk {i+1}:")
            print(chunk_text[:500])  # Display first 500 characters
            print("-" * 60)

            # Check for issues
            if len(chunk_text) < 100:
                print("⚠️ Warning: Chunk is too short, might be incomplete.")
            if "figure" in chunk_text.lower() or "table" in chunk_text.lower():
                print("⚠️ Warning: Chunk contains references to figures/tables.")
            if chunk_text.count(".") < 2:  # If chunk has fewer than 2 sentences
                print("⚠️ Warning: Possible incomplete chunk (too few sentences).")

        print("=" * 80)

# 🔹 RUN SCRIPT
if __name__ == "__main__":
    chunked_text_folder = "D:\\RAG_Paper_Analyzer\\chunked_text"
    analyze_json_chunks(chunked_text_folder)
