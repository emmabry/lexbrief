from sklearn.metrics import precision_recall_fscore_support
import numpy as np

def load_docs(path):
    docs = []
    with open(path) as f:
        for line in f:
            if line.strip():
                docs.append([int(x) for x in line.strip().split()])
    return docs

gold_docs = load_docs("./data/eur-lexsum/processed-data/val-textrank_oracle_labels.txt")
pred_docs = load_docs("./data/eur-lexsum/processed-data/val-base-distilbert_preds.txt")

assert len(gold_docs) == len(pred_docs), f"Mismatch: {len(gold_docs)} vs {len(pred_docs)} docs"

precisions, recalls, f1s = [], [], []
for y_true, y_pred in zip(gold_docs, pred_docs):
    assert len(y_true) == len(y_pred), "Sentence count mismatch"
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    precisions.append(p)
    recalls.append(r)
    f1s.append(f)

print("Macro Precision:", np.mean(precisions))
print("Macro Recall:   ", np.mean(recalls))
print("Macro F1:       ", np.mean(f1s))


'''
LEGALBERT:
Macro Precision: 0.7143
Macro Recall:    0.7668
Macro F1:        0.7257

ROBERTA:
Macro Precision: 0.7043
Macro Recall:    0.6957
Macro F1:        0.6842

DISTILBERT:
Macro Precision: 0.7125
Macro Recall:    0.7360
Macro F1:        0.7092

Unsupervised DistilBERT:
Macro Precision: 0.4687
Macro Recall:    0.4850
Macro F1:        0.4070

LEAD-3 BASELINE:
Macro Precision: 0.5392
Macro Recall:    0.5188
Macro F1:        0.4458
'''

