from eurlex import get_data_by_celex_id, get_articles_by_celex_id
from fastapi import FastAPI
import re

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "This is a test message!"}

# Testing out packages for retrieving EUR-Lex data
@app.get("/eurlex")
async def eurlex():
    data = get_data_by_celex_id('32025D1267')
    preamble = data['preamble']['text']
    articles = [data['articles'][i]['text'] for i in range(len(data['articles']))]
    text = preamble + '\n\n' + '\n\n'.join(articles)
    related_documents = data['related_documents']
    print(text)
    print(related_documents)
    title = re.sub(r'\s+', ' ', data['title'].replace('\n', '')).strip()

    return data