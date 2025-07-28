from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
distilbert_model_path = "./models/distilbert-summarisation-v1"
distilbert_model = DistilBertForSequenceClassification.from_pretrained(distilbert_model_path).to(DEVICE)
distilbert_tokenizer = DistilBertTokenizer.from_pretrained(distilbert_model_path)
distilbert_model.eval()

def distilbert_extract(text, max_tokens=1024):
    from nltk.tokenize import sent_tokenize
    sentences = sent_tokenize(text)
    
    selected_sents = []
    current_tokens = 0
    
    for sent in sentences:
        inputs = distilbert_tokenizer(sent, truncation=True, padding=True, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = distilbert_model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        if pred == 1:
            tokens = len(distilbert_tokenizer(sent)["input_ids"])
            if current_tokens + tokens <= max_tokens:
                selected_sents.append(sent)
                current_tokens += tokens
            else:
                break

    return " ".join(selected_sents)
