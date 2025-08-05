import { useState } from 'react';

type CelexData = {
    title: string;
    text: string;
    related_documents: string[];
  };
  
  type ChatProps = {
    celexData: CelexData;
  };

function Chat({ celexData }: ChatProps) {
  const [messages, setMessages] = useState<string[]>([]);
  const [responses, setResponses] = useState<string[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function submitNewMessage(newMessage: string) {
    setMessages([...messages, newMessage]);
    setNewMessage('');
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/ask_question`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
          },          
        body: JSON.stringify({
            question: newMessage,
            text: celexData?.text,
          })
      });
      if (!response.ok) {
        throw new Error('Error fetching response');
      }

      const data = await response.json();
      setResponses([...responses, data.response]);
    } catch (error) {
      console.error('Error submitting message:', error);
    } finally {
      setIsLoading(false);
    }

  }

  return (
    <div>
      {messages.length === 0 && (
        <p className="text-muted">Ask questions about the document or request summaries.</p>
      )}
      {messages.length > 0 && (
        <div className="chat-header">
            
        </div>
            )}
        {messages.map((message, index) => (
            <div key={index} className="chat-message">
                <div className="message-text border p-2">{message}</div>
                {isLoading && index === messages.length - 1 ? (
                    <div className="loading-spinner">
                        <span className="spinner-border spinner-border-sm" role="status"></span>
                        </div>
                        ) : responses[index] ? (
                        <div className="response-text border p-2">{responses[index]}</div>
                        ) : null}

            </div>
        ))}
      <form
        className="p-2 d-flex"
        onSubmit={(e) => {
          e.preventDefault();
          submitNewMessage(newMessage);
        }}
      >
          <input
          className="form-control me-2 flex-grow-1"
          type="text"
          placeholder="e.g. What is the main purpose of this document?"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          />
            <button className="btn my-button d-flex align-items-center h-10 px-4 py-2" type="submit">
                Send
            </button>
        </form>
    </div>
  );
}

export default Chat;