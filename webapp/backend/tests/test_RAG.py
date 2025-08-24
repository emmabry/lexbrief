from unittest.mock import patch
from RAG import ask_legal_question

@patch("RAG.OllamaLLM.invoke")
@patch("RAG.start_ollama_server")
@patch("RAG.parse_document")
def test_ask_legal_question(mock_parse, mock_start, mock_invoke):
    mock_start.return_value = None
    mock_invoke.return_value = "Legal answer"
    
    class MockVectorStore:
        def similarity_search(self, question, k):
            from langchain.schema import Document
            return [Document(page_content="Doc excerpt 1"), Document(page_content="Doc excerpt 2")]
    
    mock_parse.return_value = MockVectorStore()
    
    response = ask_legal_question("Doc text", "What is the obligation?")
    assert "Legal answer" == response
