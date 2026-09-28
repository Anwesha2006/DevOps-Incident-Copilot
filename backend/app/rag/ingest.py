from sentence_transformers import sentenceTransformer
from pathlib import Path
from pypdf import PdfReader
import faiss
import json
DOCUMENTS_DIR = Path("./data/incidents")
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
    for pdf_path DOCUMENTS_DIR.glob("*.pdf"):
        pages=extract_text_from_pdf(pdf_path)
        documents.extend(pages)
if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} pages")
def chunk_text(text,chunk_size=100,overlap=10):
    chunks=[]
    start=0
    while(start<len(words)):
        words=text.split()
        end=start+chunk_size;
        chunk="".join(words[start:end])
        chunks.append(chunk)
        start+=chunk_size-overlap
    return chunks
