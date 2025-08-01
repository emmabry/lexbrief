from eurlex import get_data_by_celex_id, get_articles_by_celex_id
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pdfminer.high_level import extract_text
from langdetect import detect
from models import QARequest, SumRequest
from summarisation import summarise_text
from RAG import ask_legal_question
import tempfile
import re

app = FastAPI()
# test
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "This is a test message!"}

# Testing out packages for retrieving EUR-Lex data
@app.get("/eurlex/{celex_id}")
async def eurlex(celex_id: str): 
    try:   
        data = get_data_by_celex_id(celex_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching data for CELEX ID {celex_id}: {str(e)}")
    preamble = data['preamble']['text']
    articles = [data['articles'][i]['text'] for i in range(len(data['articles']))]
    text = preamble + '\n\n' + '\n\n'.join(articles)
    related_documents = data['related_documents']
    title = re.sub(r'\s+', ' ', data['title'].replace('\n', '')).strip()
    return {'title': title,
            'text': text,
            'related_documents': related_documents}
    
# Validate & parse uploaded PDF
@app.post("/validate_pdf")
async def validate_pdf(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    # Validate doc language is english
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        contents = await file.read()
        temp.write(contents)
        temp.flush()
        extracted_text = extract_text(temp.name)
        lang = detect(extracted_text)
        if lang != 'en':
            raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}. Only English PDFs are supported.")
    return {'text': extracted_text}   

# RAG Q&A endpoint
@app.post("/ask_question")
async def ask_question(request: QARequest):
    answer = ask_legal_question(request.text, request.question)
    return {
        "question": request.question,
        "answer": answer
    }

# Summarisation endpoint
@app.post("/summarise_text")
async def summarise_text_endpoint(request: SumRequest):
    summary = summarise_text(request.text)
    return {
        "summary": summary
    }