from sentence_transformers import SentenceTransformer
import psycopg
from pgvector.psycopg import register_vector
import os
import numpy as np
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
def get_connection():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn
def search_func(query,top_k=5):
    query_embedding=model.encode(query,show_progress_bar=True)
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                id,
                text,
                source,
                page,
                embedding <=> %s AS distance
            FROM document_chunks
            ORDER BY embedding <=> %s
            LIMIT %s;
            """,(
                query_embedding,
                query_embedding,
                top_k
            ));
        results = cur.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    query = input("Enter your question: ")
    results = search_func(query)
    print("\nSearch Results")
    print("=" * 60)
    for i, result in enumerate(results, start=1):
        document_id = result[0]
        text = result[1]
        source = result[2]
        page = result[3]
        distance = result[4]
        print(f"\nResult {i}")
        print("-" * 60)
        print(f"ID: {document_id}")
        print(f"Source: {source}")
        print(f"Page: {page}")
        print(f"Distance: {distance:.4f}")
        print("\nText:")
        print(text)
    print("\n" + "=" * 60)