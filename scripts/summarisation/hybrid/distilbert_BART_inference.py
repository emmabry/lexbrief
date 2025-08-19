import os
import re
import time
import spacy
import torch
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    pipeline
)
from rouge_score import rouge_scorer
from bert_score import score

nltk.download("punkt")
nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DISTILBERT_MODEL_PATH = "./models/legalBERT"
# Load DistilBERT model
tokenizer = BertTokenizer.from_pretrained(DISTILBERT_MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(DISTILBERT_MODEL_PATH).to(DEVICE)
model.eval()

# Load BART summarizer
bart_summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1)

def preprocess_text(text, chunk_size=1024):
    text = re.sub(
        r"\[\d+\]|\(\d+\)|Official Journal.*?L \d+/\d+|^\s*Having regard.*?\n|"
        r"^\s*Whereas.*?\n|^ANNEX.*?\n|//.*?\);",
        "",
        text,
        flags=re.MULTILINE,
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
            chunks.append(current_chunk)
            current_chunk, current_tokens = [sent], tokens
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def distilbert_extract(sentences, tokenizer, model, device, max_tokens=512):
    predictions = []
    for sent in sentences:
        inputs = tokenizer(sent, return_tensors="pt", truncation=True, padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        predictions.append(pred)

    selected = [s for s, p in zip(sentences, predictions) if p == 1]
    
    summary, total_tokens = [], 0
    for sent in selected:
        tokens = len(tokenizer(sent)["input_ids"])
        if total_tokens + tokens <= max_tokens:
            summary.append(sent)
            total_tokens += tokens
        else:
            break
    return " ".join(summary)

def bart_summarise(text):
    try:
        result = bart_summarizer(text, max_length=150, min_length=40, do_sample=False)
        return result[0]["summary_text"].strip()
    except Exception as e:
        return f"FAILED: {str(e)}"

def evaluate_summaries(preds, refs):
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    total_r1 = total_r2 = total_rl = 0.0
    for pred, ref in zip(preds, refs):
        scores = scorer.score(ref, pred)
        total_r1 += scores["rouge1"].fmeasure
        total_r2 += scores["rouge2"].fmeasure
        total_rl += scores["rougeL"].fmeasure

    n = len(preds)
    print(f"\nAverage ROUGE-1 F1: {total_r1 / n:.4f}")
    print(f"Average ROUGE-2 F1: {total_r2 / n:.4f}")
    print(f"Average ROUGE-L F1: {total_rl / n:.4f}")

    P, R, F1 = score(preds, refs, lang="en", verbose=True)
    print("Average BERTScore F1:", F1.mean().item())

if __name__ == "__main__":
    with open("./data/eur-lexsum/raw-data/val.source", encoding="utf-8") as f:
        source_docs = [line.strip() for line in f if line.strip()]
    with open("./data/eur-lexsum/raw-data/val.target", encoding="utf-8") as f:
        target_summaries = [line.strip() for line in f]

    if len(source_docs) != len(target_summaries):
        raise ValueError("Source and target summary count mismatch.")

    source_docs = source_docs[:10]
    target_summaries = target_summaries[:10]

    extracted_summaries, generated_summaries = [], []

    for idx, document in enumerate(source_docs):
        print(f"\nProcessing Document {idx + 1}/{len(source_docs)}")
        chunks = preprocess_text(document, chunk_size=1024)
        chunk_summaries = [distilbert_extract(chunk, tokenizer, model, DEVICE) for chunk in chunks]
        extractive_summary = " ".join(filter(None, chunk_summaries))
        print("Extractive Summary:\n", extractive_summary)

        abstractive_summary = bart_summarise(extractive_summary)
        print("Abstractive Summary:\n", abstractive_summary)

        extracted_summaries.append(extractive_summary.strip())
        generated_summaries.append(abstractive_summary.strip())

    with open("./data/eur-lexsum/processed-data/v2-distilbert_bart_extractive.txt", "w", encoding="utf-8") as f:
        for s in extracted_summaries:
            f.write(s + "\n===\n")

    with open("./data/eur-lexsum/processed-data/v2-distilbert_bart_abstractive.txt", "w", encoding="utf-8") as f:
        for s in generated_summaries:
            f.write(s + "\n===\n")

    evaluate_summaries(generated_summaries, target_summaries)
