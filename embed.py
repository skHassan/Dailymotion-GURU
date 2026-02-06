import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from agent.chunker import chunk_text

DOCS_DIR = Path("data/docs_raw")
OUTPUT_DIR = Path("embeddings")
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def build_embeddings():
    model = SentenceTransformer(MODEL_NAME)

    texts = []
    metadatas = []

    for file_path in DOCS_DIR.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = chunk_text(content)

        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "source": file_path.name
            })

    print(f"Embedding {len(texts)} chunks...")
    vectors = model.encode(texts, show_progress_bar=True)

    store = {
        "vectors": vectors,
        "texts": texts,
        "metadatas": metadatas
    }

    with open(OUTPUT_DIR / "store.pkl", "wb") as f:
        pickle.dump(store, f)

    print("Embedding store saved.")

if __name__ == "__main__":
    build_embeddings()
