import os
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuration
UPLOAD_FOLDER = "uploads"
VECTOR_DB_PATH = "./VectorDB"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Google Gemini LLM & embeddings
GOOGLE_API_KEY = ""  # Replace with your real key
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
prompt = hub.pull("rlm/rag-prompt")

# Global retriever object to be used in FastAPI routes
retriever = None

# Helper function to format documents for prompting
def format_docs(docs):
    return "\n\n".join(doc.page_content if hasattr(doc, 'page_content') else doc for doc in docs)

def retrieve_and_format(query):
    docs = retriever.get_relevant_documents(query)
    return format_docs(docs)

# RAG pipeline
rag_chain = (
    {"context": retrieve_and_format, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Load and process text files from uploads folder
def process_uploaded_texts():
    global retriever

    combined_text = ""
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".txt"):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                combined_text += f.read() + "\n"

    # Split into documents
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.create_documents([combined_text])

    # Create vector DB
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings_model,
        persist_directory=VECTOR_DB_PATH
    )
    retriever = vectorstore.as_retriever()
    print("Reading uploaded files:")
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".txt"):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"{filename} contents:\n{content}\n---")
