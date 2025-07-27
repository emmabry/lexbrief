import os
import nltk
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from concurrent.futures import ProcessPoolExecutor

nltk.download('punkt')

MAX_DOC_SENTENCES = 200  # max doc length for oracle generation

def get_trigrams(text):
    words = text.split()
    return set(zip(words, words[1:], words[2:]))

def greedy_extractive_summary(source_sentences, target_summary, max_sentences=32, trigram_blocking=True):
    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
    selected = []
    selected_set = set()
    selected_trigrams = set()
    current_best_score = 0.0

    for _ in range(max_sentences):
        best_gain = 0.0
        best_index = None
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

    binary_labels = [1 if i in selected_set else 0 for i in range(len(source_sentences))]
    return selected, current_best_score, binary_labels

def process_doc(args):
    source, target = args
    return greedy_extractive_summary(source, target)

def process_batch(batch_sources, batch_targets, batch):
    inputs = [(src, tgt) for src, tgt in zip(batch_sources, batch_targets)]

    all_oracle_summaries = []
    all_binary_labels = []
    total_rouge = 0.0

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_doc, item) for item in inputs]
        results = []
        for i, future in enumerate(futures):
            results.append(future.result())
            print(f"Processed {i+1}/{len(futures)} items")

    for selected, score, binary_labels in results:
        all_oracle_summaries.append(selected)
        all_binary_labels.append(binary_labels)
        total_rouge += score

    avg_rouge = total_rouge / len(results)
    print(f"Batch {batch} Average ROUGE-1: {avg_rouge:.4f}")

    with open(f"./data/eur-lexsum/processed-data/val-oracle_summaries_batch_{batch}.txt", "w", encoding="utf-8") as f:
        for summary in all_oracle_summaries:
            f.write("\n".join(summary) + "\n===\n")

    with open(f"./data/eur-lexsum/processed-data/val-oracle_labels_batch_{batch}.txt", "w", encoding="utf-8") as f:
        for labels in all_binary_labels:
            f.write(" ".join(str(label) for label in labels) + "\n")

    return avg_rouge

if __name__ == "__main__":
    with open("./data/eur-lexsum/raw-data/val.source", encoding="utf-8") as f:
        lines = f.readlines()
    source_docs = [sent_tokenize(line.strip(), language='english') for line in lines]

    with open("./data/eur-lexsum/raw-data/val.target", encoding="utf-8") as f:
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

    # Save skipped docs for record
    with open("./data/eur-lexsum/raw-data/skipped-val.source", "w", encoding="utf-8") as f:
        for doc in skipped_sources:
            for sent in doc:
                f.write(sent.strip() + "\n")
            f.write("\n")
    with open("./data/eur-lexsum/raw-data/skipped-val.target", "w", encoding="utf-8") as f:
        for tgt in skipped_targets:
            f.write(tgt.strip() + "\n")

    # Save filtered docs for oracle generation
    with open("./data/eur-lexsum/processed-data/filtered-val.source", "w", encoding="utf-8") as f:
        for doc in filtered_sources:
            for sent in doc:
                f.write(sent.strip() + "\n")
            f.write("\n")

    with open("./data/eur-lexsum/processed-data/filtered-val.target", "w", encoding="utf-8") as f:
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
    print(f"Overall average ROUGE-1: {overall_rouge:.4f}")