import nltk
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

nltk.download('punkt')

def textrank_filter(source_path, labels_path, output_source_path, output_labels_path, keep_ratio=0.75):
    # Load balanced docs
    source_docs = []
    current_doc = []
    with open(source_path, encoding="utf-8") as f:
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

    # Load labels
    with open(labels_path, encoding="utf-8") as f:
        label_docs = [list(map(int, line.strip().split())) for line in f]

    if len(source_docs) != len(label_docs):
        raise ValueError(f"Number of source docs ({len(source_docs)}) does not match number of label docs ({len(label_docs)})")

    filtered_sources = []
    filtered_labels = []

    for sentences, labels in zip(source_docs, label_docs):
        if len(sentences) <= 2:
            # Tiny doc, just keep it
            filtered_sources.append(sentences)
            filtered_labels.append(" ".join(map(str, labels)))
            continue

        # Compute similarity matrix
        tfidf = TfidfVectorizer().fit_transform(sentences)
        similarity_matrix = (tfidf * tfidf.T).toarray()

        # Build graph & rank
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)

        ranked_indices = sorted(scores, key=scores.get, reverse=True)
        keep_n = max(1, int(len(sentences) * keep_ratio))
        keep_indices = sorted(ranked_indices[:keep_n])

        # Keep filtered
        filtered_sentences = [sentences[i] for i in keep_indices]
        filtered_label_line = [labels[i] for i in keep_indices]

        filtered_sources.append(filtered_sentences)
        label_str = ""
        for lbl in filtered_label_line:
            label_str += str(lbl) + " "
        filtered_labels.append(label_str.strip())


    # Write new files
    with open(output_source_path, "w", encoding="utf-8") as f:
        for doc in filtered_sources:
            for sent in doc:
                f.write(sent + "\n")
            f.write("\n")

    with open(output_labels_path, "w", encoding="utf-8") as f:
        for line in filtered_labels:
            f.write(line + "\n")

    print(f"TextRank filtered: {len(filtered_sources)} docs saved.")

if __name__ == "__main__":
    textrank_filter(
        source_path="./data/eur-lexsum/processed-data/balanced_train.source",
        labels_path="./data/eur-lexsum/processed-data/balanced_oracle_labels.txt",
        output_source_path="./data/eur-lexsum/processed-data/textrank_train.source",
        output_labels_path="./data/eur-lexsum/processed-data/textrank_oracle_labels.txt",
        keep_ratio=0.75
    )
