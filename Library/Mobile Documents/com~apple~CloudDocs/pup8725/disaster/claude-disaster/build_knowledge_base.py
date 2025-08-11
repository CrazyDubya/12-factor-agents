import os
import pdfplumber
import glob
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

KNOWLEDGE_BASE_DIR = 'disaster_knowledge_base'
VECTOR_STORE_PATH = 'vector_store'

def build_vector_store():
    """
    Reads all .md and .pdf files, creates chunks with metadata, and saves them to a FAISS vector store.
    """
    docs = []
    print(f"Building vector store from files in {KNOWLEDGE_BASE_DIR}...")

    # Process all markdown and PDF files
    file_paths = glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, '**', '*.md'), recursive=True)
    file_paths.extend(glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, '**', '*.pdf'), recursive=True))

    for file_path in file_paths:
        content = ''
        if file_path.endswith(".pdf"):
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        content += page.extract_text() or ''
            except Exception as e:
                print(f"Could not read {file_path}: {e}")
                continue
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        if content:
            docs.append(Document(page_content=content, metadata={"source": file_path}))

    print(f"Found and processed {len(docs)} documents.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunked_docs = text_splitter.split_documents(docs)

    print(f"Created {len(chunked_docs)} text chunks.")

    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    print("Creating and saving vector store...")
    vector_store = FAISS.from_documents(chunked_docs, embedding=embeddings)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Vector store built successfully and saved to {VECTOR_STORE_PATH}")

if __name__ == '__main__':
    build_vector_store()