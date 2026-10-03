from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
import psycopg
from pgvector.psycopg import register_vector
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
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
        relevant_results=[]
        for result in results:
            distance=result[4]
            similarity=1-distance
            if similarity>=0.5:
              relevant_results.append(result)
        if not relevant_results:
            print("No relevant documents found")
    conn.close()
    return relevant_results
def keyword_search(query,top_k=5):
    conn=get_connection()
    with conn.cursor()as cur:
        cur.execute("""SELECT
        id,
        text,
        source,
        page,
        ts_rank(
        text_search,
        plainto_tsquery('english', %s)
        ) AS score
        FROM document_chunks
        WHERE text_search @@ plainto_tsquery(
        'english',
        %s
        )
        ORDER BY score DESC
        LIMIT %s;""",(
        query,
        query,
        top_k
        ))
        results=cur.fetchall()
    conn.close()
    return results
def rrf_fusion(vector_results,keyword_results,top_k=5):
    scores={}
    documents={}
    for rank,result in enumerate(vector_results,start=1):
        doc_id=result[0]
        documents[doc_id]=result
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (rank + 60)
    for rank,result in enumerate(keyword_results,start=1):
        doc_id=result[0]
        documents[doc_id]=result
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (rank + 60)
    ranked_documents = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    fused_results=[]
    for doc_id, rrf_score in ranked_documents[:top_k]:
        original_result = documents[doc_id]
        fused_results.append(
            {
                "id": original_result[0],
                "text": original_result[1],
                "source": original_result[2],
                "page": original_result[3],
                "rrf_score": rrf_score
            }
        )
    return fused_results
def hybrid_search(query, top_k=5):
    vector_results = search_func(query, top_k)
    keyword_results = keyword_search(query, top_k)
    fused_results = rrf_fusion(vector_results, keyword_results, top_k)
    return fused_results
def rerank_results(query, results, top_k=5):
    pairs=[]
    for result in results:
        pairs.append((query,result['text']))
    score=reranker.predict(pairs)
    for i, result in enumerate(results):
        result['rerank_score'] = score[i]
    return sorted(results, key=lambda x: x['rerank_score'], reverse=True)[:top_k]
def retrieve(query, top_k=5):
    fused_results = hybrid_search(query, top_k)
    reranked_results = rerank_results(query, fused_results, top_k)
    return reranked_results
if __name__ == "__main__":
    query = input("Enter your question: ")
    results = retrieve(query)
    print("\nHybrid Search Results")
    print("=" * 60)
    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("-" * 60)
        print(f"ID: {result['id']}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")
        print(f"similarity: {1 - result['rrf_score']:.6f}")
        print(f"RRF Score: {result['rrf_score']:.6f}")
        print("\nText:")
        print(result['text'])
    print("\n" + "=" * 60)