import os

RAG_PDF_DIR = os.environ.get("RAG_PDF_DIR", "rag pdfs")
CHROMA_DB_DIR = os.environ.get("CHROMA_DB_DIR", "chroma_db")
EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "4"))

# Built-in fallback knowledge when no PDF index is available
BUILTIN_SECURITY_KB = {
    "sql injection": (
        "SQL Injection (OWASP A03): Untrusted input concatenated into SQL queries. "
        "Remediation: parameterized queries/prepared statements, ORM bindings, input validation, least-privilege DB accounts."
    ),
    "xss": (
        "Cross-Site Scripting (OWASP A03): Unescaped user input rendered in HTML/JS context. "
        "Remediation: context-aware output encoding, CSP headers, sanitize with DOMPurify, avoid dangerouslySetInnerHTML."
    ),
    "command injection": (
        "OS Command Injection (OWASP A03): User input passed to shell exec/spawn. "
        "Remediation: avoid shell execution, use safe APIs, strict allowlists, run with minimal privileges."
    ),
    "idor": (
        "Insecure Direct Object Reference (OWASP A01): Missing authorization on object IDs. "
        "Remediation: enforce ownership checks server-side, use opaque IDs, centralized authz middleware."
    ),
    "deserialization": (
        "Insecure Deserialization (OWASP A08): Untrusted serialized objects executed on parse. "
        "Remediation: never deserialize untrusted data, use JSON schema validation, disable dangerous gadget chains."
    ),
    "authentication": (
        "Broken Authentication (OWASP A07): Weak session/login controls, type confusion, credential stuffing. "
        "Remediation: strict type validation, MFA, secure cookies (HttpOnly, Secure, SameSite), rate limiting."
    ),
    "ssrf": (
        "Server-Side Request Forgery (OWASP A10): Server fetches attacker-controlled URLs. "
        "Remediation: URL allowlists, block internal/metadata IPs, network egress controls."
    ),
    "csrf": (
        "Cross-Site Request Forgery (OWASP A01): Forged authenticated requests from victim browser. "
        "Remediation: anti-CSRF tokens, SameSite cookies, verify Origin/Referer headers."
    ),
}


class SecurityRAG:
    def __init__(self):
        self.embeddings = None
        self.vector_db = None
        self._initialized = False

    def _ensure_initialized(self):
        if self._initialized:
            return
        self._initialized = True

        if os.environ.get("RAG_MODE", "").lower() == "builtin":
            return

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma

            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

            if os.path.exists(CHROMA_DB_DIR) and os.listdir(CHROMA_DB_DIR):
                print("[*] Loading existing ChromaDB index...")
                self.vector_db = Chroma(
                    persist_directory=CHROMA_DB_DIR,
                    embedding_function=self.embeddings,
                )
            elif os.path.exists(RAG_PDF_DIR) and any(
                f.lower().endswith(".pdf") for f in os.listdir(RAG_PDF_DIR)
            ):
                self.build_index()
            else:
                print("[*] RAG: using built-in security knowledge base (no PDF index found).")
        except Exception as exc:
            print(f"[!] RAG initialization skipped: {exc}. Using built-in knowledge base.")

    def build_index(self):
        """Load PDFs, split text, and build the vector database."""
        try:
            from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import Chroma
        except ImportError as exc:
            print(f"[!] RAG build dependencies missing: {exc}")
            return

        if not os.path.exists(RAG_PDF_DIR):
            os.makedirs(RAG_PDF_DIR, exist_ok=True)
            print(f"[!] Created {RAG_PDF_DIR}. Add PDFs to build a custom index.")
            return

        print(f"[*] Loading documents from {RAG_PDF_DIR}...")
        loader = DirectoryLoader(RAG_PDF_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        if not documents:
            print("[!] No PDF documents found.")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(documents)

        print(f"[*] Indexing {len(chunks)} chunks into ChromaDB...")
        self.vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_DIR,
        )
        print("[+] ChromaDB index built successfully.")

    def _fallback_context(self, query_text):
        query_lower = query_text.lower()
        matches = []
        for keyword, snippet in BUILTIN_SECURITY_KB.items():
            if keyword in query_lower:
                matches.append(snippet)
        if not matches:
            matches.append(
                "General DevSecOps guidance: prioritize exploitable findings, apply defense-in-depth, "
                "validate fixes with regression tests, and map issues to OWASP Top 10 categories."
            )
        return "\n\n".join(matches[:RAG_TOP_K])

    def query(self, query_text, n_results=None):
        self._ensure_initialized()
        k = n_results or RAG_TOP_K

        if self.vector_db:
            try:
                results = self.vector_db.similarity_search(query_text, k=k)
                if results:
                    return "\n\n".join(doc.page_content for doc in results)
            except Exception as exc:
                print(f"[!] Vector search failed: {exc}")

        return self._fallback_context(query_text)


_rag_instance = SecurityRAG()


def get_rag_context(query_text):
    return _rag_instance.query(query_text)


if __name__ == "__main__":
    sample = get_rag_context("How do I fix SQL injection in Node.js?")
    print("\n--- RAG Test ---")
    print(sample[:600])
