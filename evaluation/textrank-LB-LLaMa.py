import spacy
import re
import numpy as np
import subprocess
import torch
import time
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from langchain_ollama import OllamaLLM
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx

nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])

LEGAL_BERT_MODEL = "./models/legalBERT"
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
Your task is to generate detailed, factual summaries that clearly convey the document’s purpose, obligations, scope, and legal structure.

INSTRUCTIONS:
- Do not write in the first person or refer to yourself.
- Do not say 'Here is a summary' or introduce the summary in any way.
- Do not invent information not present in the text.
- Use short, formal paragraphs.
- Avoid bullet points. Each paragraph should focus on a single aspect (e.g., purpose, legal basis, scope, exemptions, dates, obligations).
- Use neutral, formal language suitable for non-expert policy readers.
- Be comprehensive. If the text is long, your summary should be proportionally detailed.

TEXT:
{text}

SUMMARY:
'''
    )

    try:
        return llm.invoke(prompt).strip()
    except Exception as e:
        return f"Error: {str(e)}"


def textrank_filter(text, keep_ratio=0.75):
    sentences = sent_tokenize(text)
    if len(sentences) <= 2:
        return text  # tiny doc, keep all
    tfidf = TfidfVectorizer().fit_transform(sentences)
    sim_matrix = (tfidf * tfidf.T).toarray()
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_indices = sorted(scores, key=scores.get, reverse=True)
    keep_n = max(1, int(len(sentences) * keep_ratio))
    keep_indices = sorted(ranked_indices[:keep_n])
    filtered_sentences = [sentences[i] for i in keep_indices]
    return " ".join(filtered_sentences)


if __name__ == "__main__":
    start_ollama_server()

    # Load source docs
    with open("./data/eur-lexsum/raw-data/val.source", encoding="utf-8") as f:
        source_docs = [line.strip() for line in f]

    print(f"Loaded {len(source_docs)} docs for summarisation.")

    # Load target summaries
    with open("./data/eur-lexsum/raw-data/val.target", encoding="utf-8") as f:
        target_summaries = [line.strip() for line in f]

    if len(target_summaries) != len(source_docs):
        raise ValueError(f"Target and source count mismatch. Expected {len(source_docs)}, got {len(target_summaries)}")

    # Limit to first 10 docs for testing
    source_docs = source_docs[:10]
    target_summaries = target_summaries[:10]
    generated_summaries = []

    for doc_idx, document in enumerate(source_docs):
        print(f"\nProcessing document {doc_idx + 1}/{len(source_docs)}")

        # --- APPLY TEXTRANK BEFORE CHUNKING ---
        filtered_text = textrank_filter(document, keep_ratio=0.75)

        # --- CHUNKING ---
        chunks = preprocess_eurlex(filtered_text, chunk_size=1500)

        # --- EXTRACTIVE SUMMARISATION ---
        extractive_summaries = [legal_bert_extract(chunk, max_tokens=1024) for chunk in chunks]
        full_extractive_summary = " ".join(filter(None, extractive_summaries))
        print("\nExtractive Summary:\n", full_extractive_summary)

        # --- ABSTRACTIVE SUMMARISATION ---
        abstractive_summary = llama_summary(full_extractive_summary)
        print("\nAbstractive Summary:\n", abstractive_summary)

        generated_summaries.append(abstractive_summary)

    # Save summaries
    with open("./data/eur-lexsum/processed-data/ft-textrank_legalBERT_llama_summaries.txt", "w", encoding="utf-8") as f:
        for summary in generated_summaries:
            f.write(summary.strip() + "\n===\n")

    # Compute ROUGE scores
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    total_rouge1 = total_rouge2 = total_rougeL = 0.0

    for pred_sum, gold_sum in zip(generated_summaries, target_summaries):
        scores = scorer.score(gold_sum, pred_sum)
        total_rouge1 += scores['rouge1'].fmeasure
        total_rouge2 += scores['rouge2'].fmeasure
        total_rougeL += scores['rougeL'].fmeasure

    n = len(generated_summaries)
    print(f"\nAverage ROUGE-1 F1: {total_rouge1 / n:.4f}")
    print(f"Average ROUGE-2 F1: {total_rouge2 / n:.4f}")
    print(f"Average ROUGE-L F1: {total_rougeL / n:.4f}")

    # Compute BERTScore
    from bert_score import score
    P, R, F1 = score(generated_summaries, target_summaries, lang="en", verbose=True)
    print("Average BERTScore F1:", F1.mean().item())

