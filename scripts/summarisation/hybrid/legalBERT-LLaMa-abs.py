import spacy
import re
import numpy as np
from transformers import AutoTokenizer, AutoModel
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from langchain_ollama import OllamaLLM
import subprocess
import time
import requests

nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])

LEGAL_BERT_MODEL = "nlpaueb/legal-bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(LEGAL_BERT_MODEL)
model = AutoModel.from_pretrained(LEGAL_BERT_MODEL)

def check_ollama_server():
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def start_ollama_server():
    if not check_ollama_server():
        print("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    if not check_ollama_server():
        raise RuntimeError("Failed to start Ollama server. Ensure it's installed and port 11434 is free.")

def preprocess_eurlex(text, chunk_size=1024):
    text = re.sub(
        r"\[\d+\]|\(\d+\)|Official Journal.*?L \d+/\d+|^\s*Having regard.*?\n|"
        r"^\s*Whereas.*?\n|^ANNEX.*?\n|//.*?\);",
        "",
        text,
        flags=re.MULTILINE
    )
    text = re.sub(r"\s+", " ", text).strip()

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]

    chunks, current_chunk, current_tokens = [], [], 0
    for sent in sentences:
        tokens = len(tokenizer(sent)["input_ids"])
        if current_tokens + tokens <= chunk_size:
            current_chunk.append(sent)
            current_tokens += tokens
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_tokens = [sent], tokens
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def legal_bert_extract(text, sentences_count=5, max_tokens=512):
    sentences = sent_tokenize(text)
    if not sentences:
        return ""
    
    sub_chunks, current_chunk, current_tokens = [], [], 0
    for sent in sentences:
        tokens = len(tokenizer(sent)["input_ids"])
        if current_tokens + tokens <= 512:
            current_chunk.append(sent)
            current_tokens += tokens
        else:
            sub_chunks.append(" ".join(current_chunk))
            current_chunk, current_tokens = [sent], tokens
    if current_chunk:
        sub_chunks.append(" ".join(current_chunk))

    doc_embeddings = []
    for chunk in sub_chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()[0]
        doc_embeddings.append(embedding)
    doc_embedding = np.mean(doc_embeddings, axis=0)

    sentence_embeddings = []
    for sent in sentences:
        inputs = tokenizer(sent, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()[0]
        sentence_embeddings.append(embedding)

    scores = np.dot(sentence_embeddings, doc_embedding) / (
        np.linalg.norm(sentence_embeddings, axis=1) * np.linalg.norm(doc_embedding)
    )
    top_indices = np.argsort(scores)[-sentences_count:]
    top_sentences = [sentences[i] for i in sorted(top_indices)]

    summary, current_tokens = [], 0
    for sent in top_sentences:
        tokens = len(tokenizer(sent)["input_ids"])
        if current_tokens + tokens <= max_tokens:
            summary.append(sent)
            current_tokens += tokens
        else:
            break
    return " ".join(summary)

def llama_summary(text, model_name="llama3"):
    llm = OllamaLLM(model=model_name, temperature=0.1)
    prompt = (
    "You are a senior EU legal analyst. Summarize the following EU legal directive in bullet points only. "
    "Do NOT add any introduction or conclusion. Do NOT say 'here is a summary' or similar phrases. "
    "Begin immediately with bullet points. Be precise, factual, and neutral.\n\n"
    f"{text}\n\n"
    "The summary should:\n"
    "- Begin with the purpose of the directive\n"
    "- Include key legal provisions and responsibilities\n"
    "- Cover the scope and any exemptions\n"
    "- State the effective date if mentioned\n"
    "- Avoid commentary or speculation\n"
    "- Use full informative bullet points (not fragments)"
    )

    try:
        return llm.invoke(prompt).strip()
    except Exception as e:
        return f"Error: {str(e)}"

def evaluate_summary(generated, reference):
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, generated)
    return scores

if __name__ == "__main__":
    start_ollama_server()

    document = '''L_2011334EN.01000101.xml 16.12.2011 EN Official Journal of the European Union L 334/1 DIRECTIVE 2011/91/EU OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 13 December 2011 on indications or marks identifying the lot to which a foodstuff belongs (codification) (Text with EEA relevance) THE EUROPEAN PARLIAMENT AND THE COUNCIL OF THE EUROPEAN UNION, Having regard to the Treaty on the Functioning of the European Union, and in particular Article 114 thereof, Having regard to the proposal from the European Commission, After transmission of the draft legislative act to the national parliaments, Having regard to the opinion of the European Economic and Social Committee (1), Acting in accordance with the ordinary legislative procedure (2), Whereas: (1) Council Directive 89/396/EEC of 14 June 1989 on indications or marks identifying the lot to which a foodstuff belongs (3) has been substantially amended several times (4).
In the interests of clarity and rationality that Directive should be codified.
(2) The internal market comprises an area without internal frontiers in which the free movement of goods, persons, services and capital is ensured.
(3) Trade in foodstuffs occupies a very important place in the internal market.
(4) Indication of the lot to which a foodstuff belongs meets the need for better information on the identity of products.
It is therefore a useful source of information when foodstuffs are the subject of dispute or constitute a health hazard for consumers.
(5) Directive 2000/13/EC of the European Parliament and of the Council of 20 March 2000 on the approximation of the laws of the Member States relating to the labelling, presentation and advertising of foodstuffs (5) contains no provisions on indication of lot identification.
(6) At international level there is a general obligation to provide a reference to the manufacturing or packaging lot of prepackaged foodstuffs.
It is the duty of the Union to contribute to the development of international trade.
(7) It is therefore advisable to provide for rules of a general and horizontal nature in order to manage a common lot identification system.
(8) The efficiency of that system depends on its application at the various marketing stages.
It is nevertheless desirable to exclude certain products and operations, in particular those taking place at the start of the distribution network for agricultural products.
(9) It is necessary to take account of the fact that the immediate consumption upon purchase of certain foodstuffs such as ice cream in individual portions means that indicating the lot directly on the individual packaging would serve no useful purpose.
However, it should be compulsory in the case of those products to indicate the lot on the combined package.
(10) The concept of a lot implies that several sales units of a foodstuff have almost identical production, manufacture or packaging characteristics.
That concept should, therefore, not apply to bulk products or products which, owing to their individual specificity or heterogeneous nature, cannot be considered as forming a homogeneous batch.
(11) In view of the variety of identification methods used, it should be up to the trader to determine the lot and to affix the corresponding indication or mark.
(12) In order to satisfy the information requirements for which it is intended, that indication should be clearly distinguishable and recognisable as such.
(13) The date of minimum durability or ‘use by’ date, may, in conformity with Directive 2000/13/EC, serve as the lot identification, provided it is indicated precisely.
(14) This Directive should be without prejudice to the obligations of the Member States relating to the time limits for transposition into national law of the Directives set out in Annex I, Part B, HAVE ADOPTED THIS DIRECTIVE: Article 1 1.
This Directive concerns the indication which allows identification of the lot to which a foodstuff belongs.
2.
For the purposes of this Directive, ‘lot’ means a batch of sales units of a foodstuff produced, manufactured or packaged under practically the same conditions.
Article 2 1.
A foodstuff may not be marketed unless it is accompanied by an indication as referred to in Article 1(1).
2.
Paragraph 1 shall not apply: (a) to agricultural products which, on leaving the holding, are: (i) sold or delivered to temporary storage, preparation or packaging stations; (ii) transported to producers’ organisations; or (iii) collected for immediate integration into an operational preparation or processing system; (b) when, at the point of sale to the ultimate consumer, the foodstuffs are not prepackaged, are packaged at the request of the purchaser or are prepackaged for immediate sale; (c) to packagings or containers the largest side of which has an area of less than 10 cm2; (d) to individual portions of ice cream.
The indication enabling the lot to be identified shall appear on the combined package.
Article 3 The lot shall be determined in each case by the producer, manufacturer or packager of the foodstuff in question, or the first seller established within the Union.
The indication referred to in Article 1(1) shall be determined and affixed under the responsibility of one or other of those operators.
It shall be preceded by the letter ‘L’ except in cases where it is clearly distinguishable from the other indications on the label.
Article 4 When the foodstuffs are prepackaged, the indication referred to in Article 1(1) and, where appropriate, the letter ‘L’ shall appear on the prepackaging or on a label attached thereto.
When the foodstuffs are not prepackaged, the indication referred to in Article 1(1) and, where appropriate, the letter ‘L’ shall appear on the packaging or on the container or, failing that, on the relevant commercial documents.
It shall in all cases appear in such a way as to be easily visible, clearly legible and indelible.
Article 5 When the date of minimum durability or ‘use by’ date appears on the label, the indication referred to in Article 1(1) need not appear on the foodstuff, provided that the date consists at least of the uncoded indication of the day and the month in that order.
Article 6 This Directive shall apply without prejudice to the indications laid down by specific provisions of the Union.
The Commission shall publish and keep up to date a list of the provisions in question.
Article 7 Directive 89/396/EEC, as amended by the Directives listed in Annex I, Part A, is repealed, without prejudice to the obligations of the Member States relating to the time limits for transposition into national law of the Directives set out in Annex I, Part B. References to the repealed Directive shall be construed as references to this Directive and shall be read in accordance with the correlation table in Annex II.
Article 8 This Directive shall enter into force on the 20th day following its publication in the Official Journal of the European Union.
Article 9 This Directive is addressed to the Member States.
Done at Strasbourg, 13 December 2011.
For the European Parliament The President J. BUZEK For the Council The President M. SZPUNAR (1) OJ C 54, 19.2.2011, p. 34.
(2) Position of the European Parliament of 11 May 2011 (not yet published in the Official Journal) and decision of the Council of 8 November 2011.
(3) OJ L 186, 30.6.1989, p. 21.
(4) See Annex I, Part A.
(5) OJ L 109, 6.5.2000, p. 29.
ANNEX I PART A Repealed Directive with list of its successive amendments (referred to in Article 7) Council Directive 89/396/EEC (OJ L 186, 30.6.1989, p. 21) Council Directive 91/238/EEC (OJ L 107, 27.4.1991, p. 50) Council Directive 92/11/EEC (OJ L 65, 11.3.1992, p. 32) PART B List of time limits for transposition into national law (referred to in Article 7) Directive Time limit for transposition 89/396/EEC 20 June 1990 (1) 91/238/EEC — 92/11/EEC — (1) In accordance with the first paragraph of Article 7 of Directive 89/396/EEC, as amended by Directive 92/11/EEC: ‘Member States shall, where necessary, amend their laws, regulations or administrative provisions so as to: — authorise trade in products complying with this Directive by not later than 20 June 1990, — prohibit trade in products not complying with this Directive with effect from 1 July 1992.
However, trade in products placed on the market or labelled before that date and not conforming with this Directive may continue until stocks run out.’.
ANNEX II Correlation table Directive 89/396/EEC This Directive Article 1 Article 1 Article 2(1) and (2) Article 2(1) and (2) Article 2(3) — Articles 3 to 6 Articles 3 to 6 Article 7 — — Article 7 — Article 8 Article 8 Article 9 — Annex I — Annex II ////////////$(document).ready(function () {generateTOC(true, '', 'Top', 'false');});
'''
    reference_summary = '''summary of   Directive 2011/91/EU on indications or marks identifying the lot to which a foodstuff belongs   summary    what does this directive do        —     It makes sure that consumers can trace the origin of pre-packaged foods.            —     It requires these foods to be labelled so that consumers can see which lot they come from.            —     It ensures that public health and food safety authorities can find out the origin and identity of pre-packaged foods in the event that these are the subject of a dispute or are a health hazard for consumers.            —     It sets out rules for producers, manufacturers, packagers and importers for labelling these foods using a common lot identification system.      key points    Scope   The Directive applies to all  pre-packaged foods  apart from:        —     agricultural products which are:        —     in temporary storage, preparation or packaging stations;             —     transported to producers’ organisations; or             —     collected for immediate processing.                 —     foods that are not prepackaged when on sale to the final consumer, are packaged at the purchaser's request or prepackaged for immediate sale;            —     packaging or containers whose largest side is less than 10cm  2  ;            —     individual portions of ice cream packaged together, where the lot identification must appear on the outside of the combined package.       Labelling of lots         —     Each lot must be labelled by the producer, manufacturer or packager, or the first seller based within the EU if it is imported.            —     The lot identification must be preceded by the letter ‘L’ except if is clearly distinguishable from the other information on the label.            —     The information on the label must be easily  visible  ,  clearly legible  and  indelible  .            —     There is no need to indicate the lot if the ‘use by’ date appears on the label.      from when does the directive apply  It has applied since 5 January 2012.   key term    * Lot  : a batch of sales units of a foodstuff produced, manufactured or packaged under practically the same conditions   act   Directive  2011/91/EU  of the European Parliament and of the Council of 13 December 2011 on indications or marks identifying the lot to which a foodstuff belongs (OJ L 334, 16.12.2011, pp. 1–5)
'''

    print("Processing document...")
    chunks = preprocess_eurlex(document, chunk_size=1500)
    extractive_summaries = [legal_bert_extract(chunk, sentences_count=5, max_tokens=1024) for chunk in chunks]
    full_extractive_summary = " ".join(filter(None, extractive_summaries))

    print("\nExtractive Summary:\n", full_extractive_summary)
    abstractive_summary = llama_summary(full_extractive_summary)
    print("\nAbstractive Summary:\n", abstractive_summary)

    if reference_summary:
        print("\nROUGE Scores (Extractive):")
        scores_ext = evaluate_summary(full_extractive_summary, reference_summary)
        for metric, score in scores_ext.items():
            print(f"{metric}: P={score.precision:.4f}, R={score.recall:.4f}, F1={score.fmeasure:.4f}")

        print("\nROUGE Scores (Abstractive):")
        scores_abs = evaluate_summary(abstractive_summary, reference_summary)
        for metric, score in scores_abs.items():
            print(f"{metric}: P={score.precision:.4f}, R={score.recall:.4f}, F1={score.fmeasure:.4f}")
