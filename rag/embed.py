from sentence_transformers import SentenceTransformer
from docx import Document
import pickle
import os

DATA_DIR = "data/ezgu-niyat"
EMBEDDINGS_FILE = "embeddings.pkl"

model = SentenceTransformer("BAAI/bge-m3")

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

def read_docx(file_path):
    """Extract text from docx file"""
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# ===== Read all .txt and .docx files from data directory =====
i = 0
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".txt"):
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif filename.endswith(".docx"):
        print(f"Processing file {i+1}: {filename}")
        i += 1
        file_path = os.path.join(DATA_DIR, filename)
        text = read_docx(file_path)
    else:
        continue

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
