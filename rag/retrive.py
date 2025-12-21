import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from environs import Env

env = Env()
env.read_env()
api_key = env.str("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

with open("embeddings.pkl", "rb") as f:
    data = pickle.load(f)

chunks = data["chunks"]
embeddings = np.array(data["embeddings"])

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def input_prompt(query: str) -> str:
    query_emb = embed_model.encode([query])[0]

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
