from eurlex import get_data_by_celex_id, get_summary_by_celex_id, get_articles_by_celex_id
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "This is a test message!"}

# Testing out packages for retrieving EUR-Lex data
@app.get("/eurlex")
async def eurlex():
    data = get_data_by_celex_id('32013R0575')
    print(data)
    return data

# Better for retrieving text
@app.get("/eurlex_articles")
async def eurlex_articles():
    df = get_articles_by_celex_id('32013R0575')
    print(df.head())
    return df.text
