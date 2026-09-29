from sentence_transformers import SentenceTransformer
from pathlib import Path
from pypdf import PdfReader
import json
import numpy as np
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = BASE_DIR / "data" / "incidents"
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
model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
if __name__ == "__main__":
    documents = load_documents()
    print("Loaded pages:", len(documents))
    chunks = []
    for document in documents:
        document_chunks = chunk_text(
            document["text"],
        )
        for chunk in document_chunks:
            chunks.append({
                "text": chunk,
                "source": document["source"],
                "page": document["page"]
            })
    print("Created chunks:", len(chunks))
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")
    print("Embedding shape:", embeddings.shape)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print("Vectors stored:", index.ntotal)
    # Create vector_store folder
    vector_store = Path("vector_store")
    vector_store.mkdir(exist_ok=True)
    faiss.write_index(
        index,
        "vector_store/index.faiss"
    )
    with open(
        "vector_store/metadata.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            chunks,
            f,
            indent=2
        )
    print("FAISS index saved!")
    print("Metadata saved!")


