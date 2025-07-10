import os
import nltk
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from concurrent.futures import ProcessPoolExecutor

nltk.download('punkt')

MAX_DOC_SENTENCES = 200

def get_trigrams(text):
    words = text.split()
    trigrams = set()
    for i in range(len(words) - 2):
        trigram = (words[i], words[i + 1], words[i + 2])
        trigrams.add(trigram)
    return trigrams

def greedy_extractive_summary(source_sentences, target_summary, max_sentences=32, trigram_blocking=True):
    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
    selected = []
    selected_set = set()
    selected_trigrams = set()
    current_best_score = 0.0

    for i in range(max_sentences):
        best_gain = 0.0
        best_idx = None
        best_score = current_best_score

        for index, sentence in enumerate(source_sentences):
            if index in selected_set:
                continue

            if trigram_blocking and (get_trigrams(sentence) & selected_trigrams):
                continue

            candidate_summary = ' '.join(selected + [sentence])
            score = scorer.score(target_summary, candidate_summary)['rouge1'].fmeasure
            gain = score - current_best_score

            if gain > best_gain:
                best_gain = gain
                best_index = index
                best_score = score

        if best_index is None or best_gain <= 0:
            break

        selected_set.add(best_index)
        selected.append(source_sentences[best_index])
        selected_trigrams.update(get_trigrams(source_sentences[best_index]))
        current_best_score = best_score

    binary_labels = [1 if sentence in selected else 0 for sentence in source_sentences]

    return selected, current_best_score, binary_labels

def process_doc(args):
    source, target = args
    return greedy_extractive_summary(source, target)

def process_batch(batch_sources, batch_targets, batch):

    inputs = []
    for i in range(len(batch_sources)):
        inputs.append((batch_sources[i], batch_targets[i]))

    all_oracle_summaries = []
    all_binary_labels = []
    total_rouge = 0.0

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = []
        for item in inputs:
            futures.append(executor.submit(process_doc, item))
    
        results = []
        for i, future in enumerate(futures):
            results.append(future.result())
            print(f"Processed {i+1}/{len(futures)} items")

    for selected, score, binary_labels in results:
        all_oracle_summaries.append(selected)
        all_binary_labels.append(binary_labels)
        total_rouge += score

    avg_rouge = total_rouge / len(results)
    print(f"Batch {batch} Average ROUGE-1 score: {avg_rouge:.4f}")

    with open(f"./data/eur-lexsum/processed-data/oracle_summaries_batch_{batch}.txt", "w", encoding="utf-8") as f:
        for summary in all_oracle_summaries:
            f.write("\n".join(summary) + "\n===\n")

    with open(f"./data/eur-lexsum/processed-data/oracle_labels_batch_{batch}.txt", "w", encoding="utf-8") as f:
        for labels in all_binary_labels:
            label_str = ""
            for label in labels:
                label_str += str(label) + " "
                f.write(label_str.strip() + "\n")


    return avg_rouge

if __name__ == "__main__":
    with open("./data/eur-lexsum/raw-data/train.source", encoding="utf-8") as f:
        lines = f.readlines()
    source_docs = [sent_tokenize(line.strip(), language='english') for line in lines]

    with open("./data/eur-lexsum/raw-data/train.target", encoding="utf-8") as f:
        target_summaries = [line.strip() for line in f]

    filtered_sources = []
    filtered_targets = []
    skipped_sources = []
    skipped_targets = []

    for source, target in zip(source_docs, target_summaries):
        if len(source) <= MAX_DOC_SENTENCES:
            filtered_sources.append(source)
            filtered_targets.append(target)
        else:
            skipped_sources.append(source)
            skipped_targets.append(target)

    print(f"Kept {len(filtered_sources)} / {len(source_docs)} docs")
    print(f"Skipped {len(skipped_sources)} docs")

    # Save skipped docs for later
    with open("./data/eur-lexsum/raw-data/skipped.source", "w", encoding="utf-8") as f:
        for doc in skipped_sources:
            for sentence in doc:
                f.write(sentence.strip() + "\n")
            f.write("\n")
    with open("./data/eur-lexsum/raw-data/skipped.target", "w", encoding="utf-8") as f:
        for target in skipped_targets:
            f.write(target.strip() + "\n")

    # Save filtered docs for later
    with open("./data/eur-lexsum/processed-data/filtered.source", "w", encoding="utf-8") as f:
        for doc in filtered_sources:
            for sentence in doc:
                f.write(sentence.strip() + "\n")
            f.write("\n")  # blank line separates documents

    with open("./data/eur-lexsum/processed-data/filtered.target", "w", encoding="utf-8") as f:
        for tgt in filtered_targets:
            f.write(tgt.strip() + "\n")

    batch_size = 300
    num_batches = (len(filtered_sources) + batch_size - 1) // batch_size

    overall_rouge = 0.0

    for batch in range(num_batches):
        start = batch * batch_size
        end = min((batch + 1) * batch_size, len(filtered_sources))

        batch_sources = filtered_sources[start:end]
        batch_targets = filtered_targets[start:end]

        avg_rouge = process_batch(batch_sources, batch_targets, batch)
        overall_rouge += avg_rouge * len(batch_sources)

    overall_rouge /= len(filtered_sources)
    print(f"Overall average ROUGE-1 score: {overall_rouge:.4f}")
