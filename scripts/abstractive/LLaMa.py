import spacy
import re
import numpy as np
from transformers import AutoTokenizer, AutoModel
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from langchain_ollama import OllamaLLM
import subprocess
import time
import requests

nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])

LEGAL_BERT_MODEL = "nlpaueb/legal-bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(LEGAL_BERT_MODEL)
model = AutoModel.from_pretrained(LEGAL_BERT_MODEL)

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
            current_chunk, current_tokens = [sent], tokens
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def legal_bert_extract(text, sentences_count=5, max_tokens=512):
    sentences = sent_tokenize(text)
    if not sentences:
        return ""
    
    sub_chunks, current_chunk, current_tokens = [], [], 0
    for sent in sentences:
        tokens = len(tokenizer(sent)["input_ids"])
        if current_tokens + tokens <= 512:
            current_chunk.append(sent)
            current_tokens += tokens
        else:
            sub_chunks.append(" ".join(current_chunk))
            current_chunk, current_tokens = [sent], tokens
    if current_chunk:
        sub_chunks.append(" ".join(current_chunk))
        
    print(f"Extracting from chunk with {len(sentences)} sentences")


    doc_embeddings = []
    for chunk in sub_chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()[0]
        doc_embeddings.append(embedding)
    doc_embedding = np.mean(doc_embeddings, axis=0)

    sentence_embeddings = []
    for sent in sentences:
        inputs = tokenizer(sent, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()[0]
        sentence_embeddings.append(embedding)

    scores = np.dot(sentence_embeddings, doc_embedding) / (
        np.linalg.norm(sentence_embeddings, axis=1) * np.linalg.norm(doc_embedding)
    )
    top_indices = np.argsort(scores)[-sentences_count:]
    top_sentences = [sentences[i] for i in sorted(top_indices)]

    summary, current_tokens = [], 0
    for sent in top_sentences:
        tokens = len(tokenizer(sent)["input_ids"])
        if current_tokens + tokens <= max_tokens:
            summary.append(sent)
            current_tokens += tokens
        else:
            break
    return " ".join(summary)

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

def evaluate_summary(generated, reference):
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, generated)
    return scores

if __name__ == "__main__":
    start_ollama_server()

    source_docs = []
    with open("./data/eur-lexsum/raw-data/val.source", encoding="utf-8") as f:
        for line in f:
            source_docs.append(line)

    print(f"Loaded {len(source_docs)} docs for summarisation.")

    # Load target summaries
    target_summaries = []
    with open("./data/eur-lexsum/raw-data/val.target", encoding="utf-8") as f:
        for line in f:
            target_summaries.append(line.strip())

    if len(target_summaries) != len(source_docs):
        raise ValueError(f"Target and source count mismatch. Expected {len(source_docs)}, got {len(target_summaries)}")

    # Limit to first 50 docs for testing
    source_docs = source_docs[:10]
    target_summaries = target_summaries[:10]
    generated_summaries = []

    for doc_idx, document in enumerate(source_docs):
        print(f"Processing document {doc_idx + 1}/{len(source_docs)}")

        # Chunk document using your preprocess (adjust chunk_size to LLaMA context, e.g. 8000 tokens)
        chunks = preprocess_eurlex(document, chunk_size=8000)

        # Instead of extractive summarisation, concatenate chunks into one string
        full_text = " ".join(chunks)

        # Directly summarize full_text with LLaMA
        abstractive_summary = llama_summary(full_text)

        print("\nAbstractive Summary:\n", abstractive_summary)
        generated_summaries.append(abstractive_summary)

    with open("./data/eur-lexsum/processed-data/v2-llama_direct_summaries.txt", "w", encoding="utf-8") as f:
        for summary in generated_summaries:
            f.write(summary.strip() + "\n===\n")

    # Evaluate with ROUGE
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    total_rouge1 = 0.0
    total_rouge2 = 0.0
    total_rougeL = 0.0

    for pred_sum, gold_sum in zip(generated_summaries, target_summaries):
        scores = scorer.score(gold_sum, pred_sum)
        total_rouge1 += scores['rouge1'].fmeasure
        total_rouge2 += scores['rouge2'].fmeasure
        total_rougeL += scores['rougeL'].fmeasure

    n = len(generated_summaries)
    print(f"\nAverage ROUGE-1 F1: {total_rouge1 / n:.4f}")
    print(f"Average ROUGE-2 F1: {total_rouge2 / n:.4f}")
    print(f"Average ROUGE-L F1: {total_rougeL / n:.4f}")

    # Evaluate with BERTScore
    from bert_score import score

    P, R, F1 = score(generated_summaries, target_summaries, lang="en", verbose=True)
    print("Average BERTScore F1:", F1.mean().item())

'''
Average ROUGE-1 F1: 0.2895
Average ROUGE-2 F1: 0.0839
Average ROUGE-L F1: 0.1446
Average BERTScore F1: 0.8050
'''
