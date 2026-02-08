import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from environs import Env
from django.conf import settings
from pathlib import Path

EMB_PATH = "/root/diagno_kiosk/kiosk/rag/embeddings.pkl"

env = Env()
env.read_env()
api_key = env.str("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

with open(EMB_PATH, "rb") as f:
    data = pickle.load(f)

chunks = data["chunks"]
raw_embeddings = data["embeddings"]

# Filter embeddings to only include valid ones with consistent shape
embed_model = SentenceTransformer("BAAI/bge-m3")
expected_dim = embed_model.get_sentence_embedding_dimension()

valid_embeddings = []
valid_chunks = []
for emb, chunk in zip(raw_embeddings, chunks):
    if isinstance(emb, (list, np.ndarray)) and len(emb) == expected_dim:
        valid_embeddings.append(emb)
        valid_chunks.append(chunk)

embeddings = np.array(valid_embeddings, dtype=np.float32)
chunks = valid_chunks

def input_prompt(query: str) -> str:
    query_emb = embed_model.encode([query])[0]

    # Compute cosine similarity
    scores = np.dot(embeddings, query_emb) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb)
    )

    best_chunk = chunks[np.argmax(scores)]

    prompt = f"""
    Use the context below to answer the question.

    Context:
    {best_chunk}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
