import spacy
import re
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from langchain_ollama import OllamaLLM
import subprocess
import torch
import time
import requests

nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])

LEGAL_BERT_MODEL = "./legalBERT"
tokenizer = AutoTokenizer.from_pretrained(LEGAL_BERT_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(LEGAL_BERT_MODEL)
model.eval()

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
        raise RuntimeError("Failed to start Ollama server. Ensure it's installed and port 11434 is free.")

def preprocess_eurlex(text, chunk_size=1024):
    text = re.sub(
        r"\[\d+\]|\(\d+\)|Official Journal.*?L \d+/\d+|^\s*Having regard.*?\n|"
        r"^\s*Whereas.*?\n|^ANNEX.*?\n|//.*?\);",
        "",
        text,
        flags=re.MULTILINE
    )
    text = re.sub(r"\s+", " ", text).strip()

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]

    chunks, current_chunk, current_tokens = [], [], 0
    for sent in sentences:
        tokens = len(tokenizer(sent)["input_ids"])
        if current_tokens + tokens <= chunk_size:
            current_chunk.append(sent)
            current_tokens += tokens
        else:
            chunks.append(" ".join(current_chunk))
            overlap = 3
            overlap_start = max(0, len(current_chunk) - overlap)
            current_chunk = current_chunk[overlap_start:] + [sent]
            current_tokens = sum(len(tokenizer(s)["input_ids"]) for s in current_chunk)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def legal_bert_extract(text, max_tokens=512):
    sentences = sent_tokenize(text)
    selected_sentences = []
    current_tokens = 0

    for sent in sentences:
        inputs = tokenizer(sent, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(**inputs).logits
            pred = torch.argmax(logits, dim=1).item()
        if pred == 1:
            tokens = len(tokenizer(sent)["input_ids"])
            if current_tokens + tokens <= max_tokens:
                selected_sentences.append(sent)
                current_tokens += tokens
            else:
                break
    return " ".join(selected_sentences)

def llama_summary(text, model_name="llama3"):
    llm = OllamaLLM(model=model_name, temperature=0.1)
    prompt = (
    f'''You are a summarisation engine for official EU legal and policy documents.
Summarise the document below in two distinct sections:

SUMMARY:
- A detailed, factual summary of at least 5 sentences.
- Covers purpose, obligations, scope, and legal structure.
- Uses short, formal paragraphs (no bullet points).
- Neutral, formal language, no invented info.

KEY INSIGHTS:
- Exactly 3 to 5 concise sentences.
- Each sentence highlights a key obligation, policy aim, legal mechanism, or impact.
- Written for a non-expert reader.
- Formal and factual tone, no speculation or editorializing.
- Do not use bullet points; just sentences separated by spaces.

TEXT:
{text}

Output the SUMMARY section first, then the KEY INSIGHTS section clearly labeled.
'''
)
    try:
        return llm.invoke(prompt).strip()
    except Exception as e:
        return f"Error: {str(e)}"

def summarise_text(text):
    start_ollama_server()
    chunks = preprocess_eurlex(text, chunk_size=1500)
    extractive_summaries = [legal_bert_extract(chunk, max_tokens=1024) for chunk in chunks]
    full_extractive_summary = " ".join(filter(None, extractive_summaries))

    print("\nExtractive Summary:\n", full_extractive_summary)
    abstractive_summary = llama_summary(full_extractive_summary)
    print("\nAbstractive Summary:\n", abstractive_summary)
    
    return abstractive_summary