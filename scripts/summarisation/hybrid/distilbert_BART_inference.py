import torch
from transformers import pipeline
from rouge_score import rouge_scorer
from bert_score import score

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load validation documents
val_source_path = "./data/eur-lexsum/processed-data/val-balanced_train.source"
val_labels_path = "./data/eur-lexsum/processed-data/val-balanced_oracle_labels.txt"
val_target_path = "./data/eur-lexsum/processed-data/filtered-val.target"

documents = []
current = []
with open(val_source_path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line == "":
            if current:
                documents.append(current)
                current = []
        else:
            current.append(line)
if current:
    documents.append(current)

with open(val_labels_path, encoding="utf-8") as f:
    label_data = [list(map(int, line.strip().split())) for line in f]

with open(val_target_path, encoding="utf-8") as f:
    reference_summaries = [line.strip() for line in f]

assert len(documents) == len(label_data) == len(reference_summaries), "Length mismatch across inputs"

# Load abstractive summariser
summariser = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1)

input_extractions = []
generated_summaries = []

print("Generating abstractive summaries...")
for idx, (doc_sents, sent_labels) in enumerate(zip(documents, label_data), total=len(documents)):
    selected = [s for s, l in zip(doc_sents, sent_labels) if l == 1]
    if not selected:
        selected = doc_sents[:3]  

    input_text = " ".join(selected)
    try:
        result = summariser(input_text, max_length=150, min_length=40, do_sample=False)
        summary = result[0]["summary_text"]
    except Exception as e:
        summary = "FAILED: " + str(e)

    input_extractions.append(input_text.strip())
    generated_summaries.append(summary.strip())

# Save outputs
with open("./data/eur-lexsum/processed-data/val-bert_preds.txt", "w", encoding="utf-8") as f:
    for item in input_extractions:
        f.write(item + "\n")

with open("./data/eur-lexsum/processed-data/val-bert_summaries.txt", "w", encoding="utf-8") as f:
    for summary in generated_summaries:
        f.write(summary + "\n")

# ROUGE Evaluation
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
rouge_totals = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}

for pred, ref in zip(generated_summaries, reference_summaries):
    scores = scorer.score(ref, pred)
    for k in rouge_totals:
        rouge_totals[k] += scores[k].fmeasure

n = len(generated_summaries)
print("\nROUGE Scores:")
for k in rouge_totals:
    avg = rouge_totals[k] / n
    print(f"{k}: {avg:.4f}")

# BERTScore Evaluation
P, R, F1 = score(generated_summaries, reference_summaries, lang="en", verbose=True)
print(f"\nBERTScore F1: {F1.mean().item():.4f}")


'''
ROUGE Scores:
rouge1: 0.5084
rouge2: 0.1863
rougeL: 0.2124

BERTScore F1: 0.8086
'''