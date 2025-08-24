from fastapi.testclient import TestClient
from unittest.mock import patch
from app import app

client = TestClient(app)

@patch("app.get_data_by_celex_id")
def test_eurlex_endpoint(mock_get):
    mock_get.return_value = {
        "title": "Test Title",
        "preamble": {"text": "Preamble text"},
        "articles": [{"text": "Article 1"}],
        "related_documents": ["doc1"]
    }
    response = client.get("/eurlex/123")
    assert response.status_code == 200
    data = response.json()
    assert "Test Title" in data["title"]
    assert "Preamble text" in data["text"]

@patch("app.ask_legal_question")
def test_ask_question_endpoint(mock_ask):
    mock_ask.return_value = "Legal answer"
    payload = {"text": "Doc text", "question": "What is the obligation?"}
    response = client.post("/ask_question", json=payload)
    assert response.status_code == 200
    assert response.json()["response"] == "Legal answer"

@patch("app.summarise_text")
def test_summarise_text_endpoint(mock_summarise):
    mock_summarise.return_value = "Abstractive summary"
    payload = {"text": "Some legal text."}
    response = client.post("/summarise_text", json=payload)
    assert response.status_code == 200
    assert "Abstractive summary" in response.json()["summary"]
