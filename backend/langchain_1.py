import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
QDRANT_URL      = os.getenv("QDRANT_URL")
QDRANT_API_KEY  = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "hr_resumes"
RESUMES_FOLDER  = "./resumes"


def load_resumes(folder_path: str):
    all_documents = []
 
    # Get all PDF files in the folder
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
 
    if not pdf_files:
        print("❌ No PDF files found in /resumes folder")
        return []
 
    for pdf_file in pdf_files:
        full_path = os.path.join(folder_path, pdf_file)
        print(f"📄 Loading: {pdf_file}")
 
        # PyPDFLoader reads PDF and returns list of Document objects
        # Each Document has:
        #   .page_content  → the text of that page
        #   .metadata      → {"source": "path", "page": 0}
        loader = PyPDFLoader(full_path)
        documents = loader.load()
 
        # Add the filename as metadata so we know which resume it came from
        for doc in documents:
            doc.metadata["resume_name"] = pdf_file
 
        all_documents.extend(documents)
        print(f"   ✅ Loaded {len(documents)} pages")
 
    print(f"\n📚 Total pages loaded: {len(all_documents)}")
    return all_documents
 
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        # It tries to split by these separators in order
        # so it prefers splitting at paragraphs, then sentences
        separators=["\n\n", "\n", ".", " "]
    )
 
    chunks = splitter.split_documents(documents)
    print(f"✂️  Split into {len(chunks)} chunks")
    return chunks

def get_embeddings():
    print("🔢 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("✅ Embedding model ready")
    return embeddings

def store_in_qdrant(chunks, embeddings):
    print("\n📦 Connecting to Qdrant...")
 
    # Connect to your Qdrant cloud cluster
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
 
    # Create collection if it doesn't exist
    # size=384 because "all-MiniLM-L6-v2" creates 384-dim vectors
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        print(f"🆕 Creating collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,               # must match your embedding model
                distance=Distance.COSINE  # cosine similarity for text
            )
        )
    else:
        print(f"✅ Collection '{COLLECTION_NAME}' already exists")
 
    # Store all chunks as vectors in Qdrant
    print("⬆️  Uploading vectors to Qdrant...")
    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
    )
 
    print(f"✅ Stored {len(chunks)} chunks in Qdrant\n")
    return vectorstore


def load_from_qdrant(embeddings):
    print("📥 Loading existing vectorstore from Qdrant...")
    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
    )
    print("✅ Vectorstore loaded\n")
    return vectorstore
 
def build_rag_chain(vectorstore):
 
    # Retriever: searches Qdrant for top 4 most relevant chunks
    # search_type="similarity" uses cosine similarity
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}   # return top 4 chunks
    )
 
    # Prompt: tells LLM to act as HR assistant
    # {context} = the retrieved resume chunks
    # {question} = the HR's question
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert HR assistant helping to screen resumes.
You will be given resume content as context and a question from HR.
Answer based ONLY on the provided resume context.
Always mention the candidate's name when referring to them.
If the information is not in the context, say 'Not found in the provided resumes'.
Be concise and structured in your answers."""),
        ("human", """Resume context:
{context}
 
HR Question: {question}""")
    ])
 
    # LLM: Groq with Llama — fast and free
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,        # 0 = factual, consistent answers
        api_key=GROQ_API_KEY
    )
 
    # Helper to format retrieved chunks into a single string
    def format_context(docs):
        formatted = []
        for doc in docs:
            resume_name = doc.metadata.get("resume_name", "Unknown")
            formatted.append(f"--- From: {resume_name} ---\n{doc.page_content}")
        return "\n\n".join(formatted)
 
    # Build the full RAG chain using LCEL pipe syntax
    # RunnablePassthrough() just passes the question through unchanged
    rag_chain = (
        {
            "context": retriever | format_context,  # retrieve → format
            "question": RunnablePassthrough()        # pass question as-is
        }
        | prompt          # fill context + question into prompt
        | llm             # send to Groq
        | StrOutputParser() # extract plain string
    )
 
    return rag_chain
 



def main():
    print("=" * 55)
    print("   HR RESUME RAG SYSTEM")
    print("=" * 55)
 
    # -- Embeddings (always needed)
    embeddings = get_embeddings()
 
    # -- Choose one of these two options:
    #
    # OPTION A: First time — load PDFs and upload to Qdrant
    #   Use this when you add new resumes
    #
    # OPTION B: Already uploaded — just load from Qdrant
    #   Use this for everyday querying (faster)
 
    print("\nDo you want to:")
    print("  1. Upload new resumes to Qdrant (first time / new resumes)")
    print("  2. Query existing resumes already in Qdrant")
    choice = input("\nEnter 1 or 2: ").strip()
 
    if choice == "1":
        # OPTION A — Upload
        os.makedirs(RESUMES_FOLDER, exist_ok=True)
        documents = load_resumes(RESUMES_FOLDER)
        if not documents:
            return
        chunks = split_documents(documents)
        vectorstore = store_in_qdrant(chunks, embeddings)
 
    elif choice == "2":
        # OPTION B — Load existing
        vectorstore = load_from_qdrant(embeddings)
 
    else:
        print("Invalid choice. Exiting.")
        return
 
    # -- Build the RAG chain
    print("🔗 Building RAG chain...")
    rag_chain = build_rag_chain(vectorstore)
    print("✅ RAG chain ready!\n")
 
    # -- HR Question Loop
    print("=" * 55)
    print("   ASK QUESTIONS ABOUT CANDIDATES")
    print("   Type 'exit' to quit")
    print("=" * 55)
 
    # Example questions you can ask:
    # - "Which candidates know Python?"
    # - "Who has experience with machine learning?"
    # - "Which candidate has the most years of experience?"
    # - "Who has worked at a startup?"
    # - "List all candidates with a master's degree"
 
    while True:
        question = input("\n🧑‍💼 HR Question: ").strip()
 
        if question.lower() == "exit":
            print("Goodbye!")
            break
 
        if not question:
            continue
 
        print("\n🤔 Searching resumes and generating answer...\n")
        answer = rag_chain.invoke(question)
        print(f"🤖 Answer:\n{answer}")
        print("-" * 55)
 
 
if __name__ == "__main__":
    main()
 
