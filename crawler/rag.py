import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "default")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def run_rag_pipeline(markdown_path, faiss_index_path, character_name, game_name, query):
    """Run RAG pipeline: ingest markdown, create/load FAISS, process query."""
    # Normalize path to avoid slash issues
    markdown_path = os.path.normpath(markdown_path)
    faiss_index_path = os.path.normpath(faiss_index_path)
    
    print(f"Attempting to load markdown file: {markdown_path}")
    if not os.path.exists(markdown_path):
        print(f"Error: Markdown file not found at {markdown_path}")
        return None

    vector_store = None
    if os.path.exists(faiss_index_path):
        embeddings = OllamaEmbeddings(model="llama3")
        vector_store = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
        return process_query(vector_store, character_name, game_name, query)
    
    try:
        loader = TextLoader(markdown_path, encoding="utf-8")
        docs = loader.load()
        embeddings = OllamaEmbeddings(model="llama3")
        chunker = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)
        chunked_docs = chunker.split_documents(docs)
        vector_store = FAISS.from_documents(chunked_docs, embeddings, distance_strategy="COSINE")
        os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)
        vector_store.save_local(faiss_index_path)
        print(f"FAISS index saved to: {faiss_index_path}")
        return process_query(vector_store, character_name, game_name, query)
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        return None

def process_query(vector_store, character_name, game_name, query):
    """Process query using RAG chain with Google Gemini API."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = ChatPromptTemplate.from_template(
        """Provide a concise summary answering the question about {character_name} from the game {game_name} based on the context. Focus on relevant details about the character's role, background, or actions related to the question.

        Context: {context}

        Question: {question}

        Summary:
        """
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough(), "character_name": lambda _: character_name, "game_name": lambda _: game_name}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain.invoke(query)