import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

RAG_PDF_DIR = "rag pdfs"
CHROMA_DB_DIR = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class SecurityRAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_db = None
        self._initialize_db()

    def _initialize_db(self):
        """Initializes or loads the ChromaDB vector database."""
        if not os.path.exists(CHROMA_DB_DIR):
            print("[*] ChromaDB not found. Creating new database...")
            self.build_index()
        else:
            print("[*] Loading existing ChromaDB...")
            self.vector_db = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=self.embeddings
            )

    def build_index(self):
        """Loads PDFs, splits text, and builds the vector database."""
        if not os.path.exists(RAG_PDF_DIR):
            os.makedirs(RAG_PDF_DIR)
            print(f"[!] Warning: {RAG_PDF_DIR} was missing. Created it. Add PDFs to index them.")
            return

        print(f"[*] Loading documents from {RAG_PDF_DIR}...")
        loader = DirectoryLoader(RAG_PDF_DIR, glob="./*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()

        if not documents:
            print("[!] No PDF documents found in 'rag pdfs' folder.")
            return

        print(f"[*] Splitting {len(documents)} document pages into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        print(f"[*] Generating embeddings and storing {len(chunks)} chunks in ChromaDB...")
        self.vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        print("[+] ChromaDB index built successfully.")

    def query(self, query_text, n_results=3):
        """Queries the vector database for relevant context."""
        if not self.vector_db:
            return ""
        
        print(f"[*] Querying RAG for: {query_text[:50]}...")
        results = self.vector_db.similarity_search(query_text, k=n_results)
        
        context = "\n\n".join([doc.page_content for doc in results])
        return context

# Singleton instance
rag_system = SecurityRAG()

if __name__ == "__main__":
    # Test query
    test_context = rag_system.query("What are the OWASP Top 10 vulnerabilities?")
    print("\n--- Test Query Result ---")
    print(test_context[:500] + "...")
