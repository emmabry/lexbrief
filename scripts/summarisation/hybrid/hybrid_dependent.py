import random
from summarizer import Summarizer
from transformers import pipeline
from evaluate import load
import nltk
from tqdm import tqdm

nltk.download('punkt')

source_path = "./data/eur-lexsum/raw-data/val.source"
target_path = "./data/eur-lexsum/raw-data/val.target"

# Load all data
with open(source_path, "r", encoding="utf-8") as f:
    val_docs = [line.strip() for line in f.readlines()]

with open(target_path, "r", encoding="utf-8") as f:
    val_refs = [line.strip() for line in f.readlines()]

assert len(val_docs) == len(val_refs), "Mismatch between source and target files."

# Sample a small subset for quick testing
sample_size = 5  
indices = list(range(sample_size))
sample_docs = [val_docs[i] for i in indices]
sample_refs = [val_refs[i] for i in indices]


# Load models
extractive_model = Summarizer()
abstractive_model = pipeline("summarization", model="MikaSie/RoBERTa_BART_dependent_V1", tokenizer="MikaSie/RoBERTa_BART_dependent_V1")

generated_summaries = []
for doc in tqdm(sample_docs, desc="Generating summaries"):
    extractive_summary = extractive_model(doc)
    abstractive_summary = abstractive_model(extractive_summary, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    generated_summaries.append(abstractive_summary)

for i, (gen_sum, ref_sum) in enumerate(zip(generated_summaries, val_refs)):
    print(f"Document {i+1}:")
    print("Generated Summary:")
    print(gen_sum)
    print("Reference Summary:")
    print(ref_sum)
    print("-" * 40)

# Evaluate with ROUGE
rouge = load("rouge")
results = rouge.compute(predictions=generated_summaries, references=sample_refs)

print("ROUGE Scores (sample):")
for key, value in results.items():
    print(f"{key}: {value:.4f}")
    
'''
Using the pretrained models from the paper, it is clear that the model hallucinates and provides summaries of similar, but completely different, EUR-lex documents.
Considering this, the method does not seem to be reliable enough for production use.
'''
