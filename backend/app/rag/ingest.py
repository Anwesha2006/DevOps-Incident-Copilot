from sentence_transformers import SentenceTransformer
from pathlib import Path
from pypdf import PdfReader
import json
import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv
import os
load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = BASE_DIR / "data" / "incidents"
DATABASE_URL=os.getenv("DATABASE_URL","postgresql://postgres:postgres@localhost:5432/incident_copilot")
model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_path):
    reader=PdfReader(pdf_path)
    pages=[]
    for page_number,page in enumerate(reader.pages,start=1):
        text=page.extract_text()
        if text:
            pages.append({
                "text": text,
                "page": page_number,
                "source": pdf_path.name
            })
    return pages
def load_documents():
    documents=[]
    for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):
        pages=extract_text_from_pdf(pdf_path)
        documents.extend(pages)
    return documents
def chunk_text(text,chunk_size=100,overlap=10):
    chunks=[]
    start=0
    words=text.split()
    while(start<len(words)):
        end=start+chunk_size;
        chunk=" ".join(words[start:end])
        chunks.append(chunk)
        start+=chunk_size-overlap
    return chunks
def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn
def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                source TEXT NOT NULL,
                page INTEGER,
                embedding VECTOR(384)
            );
        """)
    conn.commit()
def store_chunks(conn, chunks, embeddings):
    with conn.cursor() as cur:
        for chunk, embedding in zip(chunks, embeddings):
            cur.execute(
                """
                INSERT INTO document_chunks
                (text, source, page, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    chunk["text"],
                    chunk["source"],
                    chunk["page"],
                    embedding
                )
            )
    conn.commit()
if __name__ == "__main__":
    documents = load_documents()
    print("Loaded pages:", len(documents))
    chunks = []
    for document in documents:
        document_chunks = chunk_text(
            document["text"],
            chunk_size=100,
            overlap=10
        )
        for chunk in document_chunks:
            chunks.append({
                "text": chunk,
                "source": document["source"],
                "page": document["page"]
            })
    print("Created chunks:", len(chunks))
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )
    embeddings = np.array(embeddings).astype("float32")
    print("Embedding shape:", embeddings.shape)
    conn = get_connection()
    create_table(conn)
    store_chunks(
        conn,
        chunks,
        embeddings
    )
    print("Vectors stored in PostgreSQL!")
    conn.close()
    print("Ingestion complete!")

