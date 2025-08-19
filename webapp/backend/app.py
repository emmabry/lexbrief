from eurlex import get_data_by_celex_id, get_articles_by_celex_id
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from models import QARequest, SumRequest
from summarisation import summarise_text
from RAG import ask_legal_question
import re

app = FastAPI()

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

@app.get("/eurlex/{celex_id}")
async def eurlex(celex_id: str): 
    try:   
        data = await run_in_threadpool(get_data_by_celex_id, celex_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching data for CELEX ID {celex_id}: {str(e)}")
    preamble = data['preamble']['text']
    articles = [data['articles'][i]['text'] for i in range(len(data['articles']))]
    text = preamble + '\n\n' + '\n\n'.join(articles)
    related_documents = data['related_documents']
    title = re.sub(r'\s+', ' ', data['title'].replace('\n', '')).strip()
    if not title:
        raise HTTPException(status_code=404, detail="No data found for the provided CELEX ID.")

    return {
        'title': title,
        'text': text,
        'related_documents': related_documents
    }
    
@app.post("/ask_question")
async def ask_question(request: QARequest):
    response = await run_in_threadpool(ask_legal_question, request.text, request.question)
    return {"question": request.question, "response": response}


@app.post("/summarise_text")
async def summarise_text_endpoint(request: SumRequest):
    summary = await run_in_threadpool(summarise_text, request.text)
    return {"summary": summary}
