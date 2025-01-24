from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scipy.spatial.distance import cosine
import requests
import streamlit as st

# Load a pre-trained embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    """Generate embeddings for the given text."""
    return model.encode(text, convert_to_tensor=True)

app = FastAPI()

# Store embedded documents
documents = {}

class Document(BaseModel):
    title: str
    content: str

@app.post("/add_document/")
def add_document(doc: Document):
    """Add a document to the embedding store."""
    embedding = embed_text(doc.content)
    documents[doc.title] = embedding
    return {"message": "Document added!"}

@app.get("/query/")
def query_document(query: str):
    """Query the document store with a user-provided query."""
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found. Please add documents first.")

    query_embedding = embed_text(query)
    results = find_closest_match(query_embedding)
    return {"results": results}

def find_closest_match(query_embedding):
    """Find the document with the closest embedding match."""
    closest = min(documents.items(), key=lambda x: cosine(query_embedding, x[1]))
    return closest[0]

def query_groq(text):
    """Send a query to the Groq API."""
    response = requests.post(
        "https://api.groq.com/query",
        json={"input": text},
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Groq API error")
    return response.json()

# Streamlit frontend
st.title("Document Embedding Chatbot")

query = st.text_input("Ask me anything:")
if st.button("Submit"):
    try:
        response = requests.get(f"http://127.0.0.1:8080/query/?query={query}")
        st.write(response.json())
    except Exception as e:
        st.error(f"Error: {e}")
