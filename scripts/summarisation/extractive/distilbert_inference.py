import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from rouge_score import rouge_scorer
import nltk

nltk.download('punkt')

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model & tokenizer
model_path = "./models/distilbert-summarisation-v1" 
model = DistilBertForSequenceClassification.from_pretrained(model_path)
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model.to(DEVICE)
model.eval()

# Load filtered source docs
source_docs = []
current_doc = []
with open("./data/eur-lexsum/processed-data/val-textrank_train.source", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line == "":
            if current_doc:
                source_docs.append(current_doc)
                current_doc = []
        else:
            current_doc.append(line)
if current_doc:
    source_docs.append(current_doc)

print(f"Loaded {len(source_docs)} docs for inference.")

# Load initial target summaries
target_summaries = []
with open("./data/eur-lexsum/processed-data/filtered-val.target", encoding="utf-8") as f:
    for line in f:
        target_summaries.append(line.strip())

assert len(target_summaries) == len(source_docs), "Target and source count mismatch"

# Inference 
predictions = []
extracted_summaries = []

for doc_idx, sentences in enumerate(source_docs):
    doc_preds = []
    for sent in sentences:
        inputs = tokenizer(sent, truncation=True, padding=True, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits  
            pred = torch.argmax(logits, dim=1).item()  
        doc_preds.append(pred)
    predictions.append(doc_preds)

    # Build extractive summary
    selected_sents = [s for s, l in zip(sentences, doc_preds) if l == 1]
    extracted_summaries.append(" ".join(selected_sents))

    print(f"Doc {doc_idx+1}/{len(source_docs)} done.")

# Save predictions
with open("./data/eur-lexsum/processed-data/val-distilbert_preds.txt", "w", encoding="utf-8") as f:
    for doc in predictions:
        f.write(" ".join(map(str, doc)) + "\n")

with open("./data/eur-lexsum/processed-data/val-distilbert_summaries.txt", "w", encoding="utf-8") as f:
    for summary in extracted_summaries:
        f.write(summary.strip() + "\n===\n")

print("Inference done. Predictions & summaries saved.")

# Compute ROUGE scores
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

total_rouge1 = 0.0
total_rouge2 = 0.0
total_rougeL = 0.0

for pred_sum, gold_sum in zip(extracted_summaries, target_summaries):
    scores = scorer.score(gold_sum, pred_sum)
    total_rouge1 += scores['rouge1'].fmeasure
    total_rouge2 += scores['rouge2'].fmeasure
    total_rougeL += scores['rougeL'].fmeasure

n = len(extracted_summaries)
avg_rouge1 = total_rouge1 / n
avg_rouge2 = total_rouge2 / n
avg_rougeL = total_rougeL / n

print(f"\nAverage ROUGE-1 F1: {avg_rouge1:.4f}")
print(f"Average ROUGE-2 F1: {avg_rouge2:.4f}")
print(f"Average ROUGE-L F1: {avg_rougeL:.4f}")

from bert_score import score

P, R, F1 = score(extracted_summaries, target_summaries, lang="en", verbose=True)

print("Average BERTScore F1:", F1.mean().item())


"""
RESULTS:
Average ROUGE-1 F1: 0.4687
Average ROUGE-2 F1: 0.1709
Average ROUGE-L F1: 0.2038
Average BERTScore F1: 0.8045
"""