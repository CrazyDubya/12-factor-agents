import os
import argparse
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

VECTOR_STORE_PATH = 'vector_store'
MODEL_NAME = 'llama3:8b'

def create_qa_chain():
    """
    Loads the vector store and creates the RetrievalQA chain.
    """
    if not os.path.exists(VECTOR_STORE_PATH):
        raise FileNotFoundError(f"Vector store not found at {VECTOR_STORE_PATH}. Please run build_knowledge_base.py first.")

    print("Loading vector store...")
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)

    print(f"Loading Ollama model: {MODEL_NAME}...")
    llm = Ollama(model=MODEL_NAME)

    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

def run_interactive_mode(qa_chain):
    print(f"\nDisaster Preparedness LLM (using {MODEL_NAME}) is ready. Type 'exit' to quit.")
    while True:
        query = input("\nAsk a question: ")
        if query.lower() == 'exit':
            break
        if query.strip():
            result = qa_chain({"query": query})
            print("\nAnswer:")
            print(result['result'].strip())

def run_single_query_mode(qa_chain, query):
    print(f"Running single query: {query}")
    result = qa_chain({"query": query})
    print("\n---AGENT_ANSWER_START---")
    print(result['result'].strip())
    print("---AGENT_ANSWER_END---")
    
    print("\n---SOURCE_DOCS_START---")
    for doc in result['source_documents']:
        print(doc.metadata.get('source', 'Unknown Source'))
    print("---SOURCE_DOCS_END---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="Run a single query and exit.")
    args = parser.parse_args()

    qa_chain = create_qa_chain()

    if args.query:
        run_single_query_mode(qa_chain, args.query)
    else:
        run_interactive_mode(qa_chain)