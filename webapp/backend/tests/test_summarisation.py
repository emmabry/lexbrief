import pytest
from unittest.mock import patch
from summarisation import summarise_text, preprocess_eurlex, legal_bert_extract

def test_preprocess_eurlex_chunks():
    text = "Sentence one. Sentence two. Sentence three."
    chunks = preprocess_eurlex(text, chunk_size=10)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)

@patch("summarisation.legal_bert_extract")
@patch("summarisation.llama_summary")
@patch("summarisation.start_ollama_server")
def test_summarise_text(mock_start, mock_llama, mock_extract):
    mock_start.return_value = None
    mock_extract.side_effect = lambda chunk, max_tokens: chunk
    mock_llama.return_value = "Abstractive summary"

    text = "This is a legal text. It contains multiple sentences."
    summary = summarise_text(text)
    assert "Abstractive summary" in summary
