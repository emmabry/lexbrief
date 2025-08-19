from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
import subprocess
import time
import requests

def check_ollama_server():
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def start_ollama_server():
    if not check_ollama_server():
        print("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    if not check_ollama_server():
        raise RuntimeError("Failed to start Ollama server.")
    
def parse_document(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators = ["\n\n", "\n", r"(?<=\. )", " ", ""]
    )
    docs = text_splitter.create_documents([text])

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cpu"}
    )

    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

def ask_legal_question(text, question, model_name="llama3.1"):
    start_ollama_server()
    vectorstore = parse_document(text)
    llm = OllamaLLM(model=model_name, temperature=0.1)
    relevant_docs = vectorstore.similarity_search(
        question, 
        k=5
    )
    context = "\n\nDOCUMENT EXCERPTS:\n" + "\n---\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"""You are a senior EU legal analyst explaining a legal document to a non-expert. Provide a complete response to the question using ONLY the provided legal document excerpts.

    {context}

    QUESTION: {question}

    RESPONSE REQUIREMENTS:
    - Answer the user's legal question based only on the document.
    - Do not use formatting or bullet points
    - Be brief and specific
    - Use direct quotes from the text when possible
    - If a legal instrument is cited, begin with: "Under [Legal Instrument]"
    - If the answer is not found in the text, say: "Not specified in document"""

    try:
        response = llm.invoke(prompt)
        print(f"debugging: {context}")
        print("----------")
        return response
        
    except Exception as e:
        return f"Error: {str(e)}"
