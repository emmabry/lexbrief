# Evaluation metrics for summarisation models.

## Extractive
### Fine-Tuned DistilBERT
- Average ROUGE-1 F1: 0.4687
- Average ROUGE-2 F1: 0.1709
- Average ROUGE-L F1: 0.2038
- Average BERTScore F1: 0.8045

### Fine-Tuned RoBERTa
- Average ROUGE-1 F1: 0.4631
- Average ROUGE-2 F1: 0.1676
- Average ROUGE-L F1: 0.2016
- Average BERTScore 0.8059

### Fine-tuned LegalBERT
- Average ROUGE-1 F1: 0.4691
- Average ROUGE-2 F1: 0.1710
- Average ROUGE-L F1: 0.2043
- Average BERTScore F1: 0.8023

Although the extractive models aren't terrible, the nature of extractive summarisation means that the resulting summaries aren't very human-readable, especially for a non-legal expert. Therefore a hybrid/abstractive summarisation model is best for this particular project.

## Hybrid
### Fine-tuned DistilBERT + LLaMa 8B
- Average ROUGE-1 F1: 0.3250
- Average ROUGE-2 F1: 0.1009
- Average ROUGE-L F1: 0.1626
- Average BERTScore F1: 0.8128

### Fine-tuned LegalBERT + LLaMa 8B
- Average ROUGE-1 F1: 0.3314
- Average ROUGE-2 F1: 0.1036
- Average ROUGE-L F1: 0.1652
- Average BERTScore F1: 0.8136

### Textrank, Fine-tuned LegalBERT + LLaMa 8B
- Average ROUGE-1 F1: 0.3237
- Average ROUGE-2 F1: 0.0978
- Average ROUGE-L F1: 0.1610
- Average BERTScore F1:  0.8126

### Fine-tuned DistilBERT + Fine-tuned BART
- Average ROUGE-1 F1: 0.2922
- Average ROUGE-2 F1: 0.0793
- Average ROUGE-L F1: 0.1523
- Average BERTScore F1:  0.8058

### Fine-tuned LegalBERT + Fine-tuned BART
- Average ROUGE-1 F1: 0.2987
- Average ROUGE-2 F1: 0.0811
- Average ROUGE-L F1: 0.1556
- Average BERTScore F1:  0.8074

- **BUT** upon inspection, the abstractive summaries are completely unrelated to the source document, and the model seems to fall back on a few distinct summaries. In a sample of 10 summaries, '2019/821' was given as the regulation number for 6 documents, and 2019/972 for 4. Even testing with an external model finetuned on the same dataset (MikaSie/RoBERTa_BART_dependent_V1), the same issue arises.

## Abstractive
### LLaMa 8B + chunking
- Average ROUGE-1 F1: 0.2895
- Average ROUGE-2 F1: 0.0839
- Average ROUGE-L F1: 0.1446
- Average BERTScore F1: 0.8050

## Conclusion