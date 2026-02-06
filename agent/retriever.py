import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
STORE_PATH = "embeddings/store.pkl"

class Retriever:
    def __init__(self):
        with open(STORE_PATH, "rb") as f:
            store = pickle.load(f)

        self.vectors = store["vectors"]
        self.texts = store["texts"]
        self.metadatas = store["metadatas"]
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, top_k: int = 4):
        query_vec = self.model.encode([query])
        scores = cosine_similarity(query_vec, self.vectors)[0]

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "text": self.texts[idx],
                "score": float(scores[idx]),
                "source": self.metadatas[idx]["source"]
            })

        return results
