from sentence_transformers import SentenceTransformer
import pickle
import os

DATA_DIR = "data/ezgu-niyat"
EMBEDDINGS_FILE = "embeddings.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")

# ===== Load existing embeddings if exist =====
if os.path.exists(EMBEDDINGS_FILE):
    with open(EMBEDDINGS_FILE, "rb") as f:
        data = pickle.load(f)
        chunks = data.get("chunks", [])
        embeddings = list(data.get("embeddings", []))
else:
    chunks = []
    embeddings = []

new_chunks = []

# ===== Read all .txt files from data directory =====
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".txt"):
        file_path = os.path.join(DATA_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        file_chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        new_chunks.extend(file_chunks)

# ===== Generate embeddings for new chunks =====
if new_chunks:
    new_embeddings = model.encode(new_chunks)
    chunks.extend(new_chunks)
    embeddings.extend(new_embeddings)

# ===== Save updated embeddings =====
with open(EMBEDDINGS_FILE, "wb") as f:
    pickle.dump(
        {
            "chunks": chunks,
            "embeddings": embeddings
        },
        f
    )

print(f"✅ Embeddings saved successfully ({len(new_chunks)} new chunks)")
