# Project plan
**Research question:** How can NLP methods be applied to improve the accessibility (readability) and understanding (factual comprehension) of complex EU policy documents for non-expert users through summarisation and question answering?

## Key Components
* Summarisation Model
* Q&A Chatbot
* GUI
* Document upload 
* Retrieve documents from EUR-Lex API

## Summarisation Model
Pure extractive pipeline has OK results:
* Average ROUGE-1 F1: 0.4687
* Average ROUGE-2 F1: 0.1709
* Average ROUGE-L F1: 0.2038
* Average BERTScore F1: 0.804

But still contains dense legal language, so isn't the most suitable option for a non-expert audience	

ChatGPT summarisation has worse ROUGE results & similar BERT results:
* Average ROUGE-1 F1: 0.2442 
* Average ROUGE-2 F1: 0.0591 
* Average ROUGE-L F1: 0.1346
* Average BERTScore F1: 0.8141

Is human-readable, but maybe at the expense of being too simple and broad. This was also a much smaller sample.

Going forth, I will aim for a hybrid approach which includes an extractive step followed by an abstractive step. If this does not produce ideal results, I will then look to ChatGPT & prompt engineering to try and strike a balance.

## Q&A Chatbot
**Using**: RAG - LLaMa 3.1
I have gotten this working decently, so the goal for this going forward is to improve performance for the web app (response times etc), and also to test out edge cases such as nonsense questions.

**Additional feature**: Pre-generate 3-5 questions after document upload to help user engage with the text.


## GUI

**Purpose:** To provide an accessible, user-friendly interface for non-experts to upload or select EU policy documents, generate a summary, and ask factual questions about the content.

**Key functions:**
* Upload or select an EU policy text (potentially via EUR-LEX API)
* Display the full text.
* Show the AI-generated summary clearly.
* Accept user-typed questions.
* Show the chatbot answer and highlight it with a supporting quote.

**Stack:**
* JavaScript React frontend
* Python FastAPI backend
* Need to find a suitable service to deploy the project


## EUR-Lex API Integration

Two main ways this will be utilised:
1. Rather than manually uploading a pdf, the user can also select/search for a policy to summarise & ask questions about within the app
2. Can be used to provide extra information about the document the user has uploaded/searched for, such as:
	* Author (Council, Commission)
	* Date of adoption
	* Relationships (linked amendments, repeals, related directives)
	* Keywords, summaries, multi-lingual versions.

**Options:**

- **EUR-Lex offical webservice**: Requires manual approval by administrator - waiting for approval.

- **pypi.org/project/eurlex-parser/**: Python package to download & parse any EUR-Lex document. 

## Potential Challenges

* **Ambiguous user questions**: Users may enter vague questions that are hard for the chatbot to interpret accurately (e.g. "What does this mean?" or "Is this good?"). Implement fallback responses when input is unclear.

* **EUR-Lex access limitations**: Use eurlex-parser as backup if official API not approved in time.

* **Parsing PDFs**: Define a pipeline to extract and clean content from official EUR-Lex PDFs. Limit accepted languages to English by extracting text & using language detection library (langdetect).


# 6 Week Timeline

## Week 1 (21 - 27 July)
* Develop and test hybrid extractive + abstractive summarisation pipeline

* Evaluate with ROUGE and BERTScore, comparing to previous baselines

* Polish RAG Q&A & integrate into backend

* Begin building out web app features: document upload & display, summary output

## Week 2 (28 Jul - 3 Aug)
* Finalise summarisation method

* Complete integration of summariser and RAG Q&A into backend pipeline

* Continue frontend development: implement question input, chatbot output

* Integrate EUR-Lex API for document search and metadata display

* Develop pre-generated questions feature

## Week 3 (4 - 10 Aug)
* Testing & bug fixing on summariser and QA pipeline integration

* Complete main web app functionality (upload/search, summarise, Q&A)

* Start internal user testing for usability and accuracy feedback

* Prepare rough demo version of the app

## Week 4 (11 - 17 Aug)
* Collect and analyse feedback from internal testing; improve models and UI

* Polish UI/UX and improve error handling and edge case coverage

* Finalize demo app version and prepare demo presentation

## Week 5 (18 - 24 Aug)
* Present working app demo

* Start writing up project report

## Week 6 (25 - 31 Aug)
* Finalise project report and documentation

* Submit report by deadline