import random

def balance_source_and_labels(source_path, labels_path, output_source_path, output_labels_path):
    random.seed(42)

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

    label_docs = []
    with open(labels_path, encoding="utf-8") as f:
        for line in f:
            nums = line.strip().split()
            nums = [int(x) for x in nums]
            label_docs.append(nums)


    if len(source_docs) != len(label_docs):
        raise ValueError(f"Number of docs mismatch: {str(len(source_docs))} source docs vs {str(len(label_docs))} label docs.")

    balanced_sources = []
    balanced_labels = []

    for i in range(len(source_docs)):
        sentences = source_docs[i]
        labels = label_docs[i]

        if len(sentences) != len(labels):
            raise Exception(f"Mismatch: {str(len(sentences))} sentences vs {str(len(labels))} labels.")

        pos_indices = []
        neg_indices = []
        for item in range(len(labels)):
            if labels[item] == 1:
                pos_indices.append(item)
            elif labels[item] == 0:
                neg_indices.append(item)

        if len(pos_indices) == 0:
            continue

        if len(pos_indices) < len(neg_indices):
            num_neg_to_keep = len(pos_indices)
        else:
            num_neg_to_keep = len(neg_indices)

        sampled_neg_indices = random.sample(neg_indices, num_neg_to_keep)

        keep_indices = pos_indices + sampled_neg_indices
        keep_indices.sort()

        balanced_sentences = []
        balanced_label_line = []
        
        for i in keep_indices:
            balanced_sentences.append(sentences[i])
            balanced_label_line.append(labels[i])

        balanced_sources.append(balanced_sentences)
        balanced_labels.append(" ".join([str(label) for label in balanced_label_line]))

    with open(output_source_path, "w", encoding="utf-8") as f:
        for doc in balanced_sources:
            for sentence in doc:
                f.write(sentence + "\n")
            f.write("\n")

    with open(output_labels_path, "w", encoding="utf-8") as f:
        for line in balanced_labels:
            f.write(line + "\n")

    print(f"Balanced: {len(balanced_sources)} docs saved.")

if __name__ == "__main__":
    balance_source_and_labels(
        source_path="./data/eur-lexsum/processed-data/filtered-val.source",
        labels_path="./data/eur-lexsum/processed-data/val-oracle_labels_merged.txt",
        output_source_path="./data/eur-lexsum/processed-data/val-balanced_train.source",
        output_labels_path="./data/eur-lexsum/processed-data/val-balanced_oracle_labels.txt"
    )
