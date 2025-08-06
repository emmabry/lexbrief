import { useState } from 'react';
import SendIcon from './assets/send.svg?react';

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
    <div className="chat d-flex flex-column justify-content-between">
      <div className="chat-messages">
        <p className="response p-2 mt-2">Hello! I'm here to help you understand this document. What would you like to know?</p>
        {messages.map((message, index) => (
            <div key={index} className="chat-message">
                <div className="message p-2">{message}</div>
                {isLoading && index === messages.length - 1 ? (
                    <div className="d-flex flex-column justify-content-start align-items-start w-100 pt-3 ps-2">
                    <p className="card-text placeholder-glow row w-100 px-2 pb-2">
                        <span className="placeholder bg-secondary col-9 mb-2 rounded-3"></span>
                        <span className="placeholder bg-secondary col-6 mb-2 rounded-3"></span>
                    </p>
                </div>
                        ) : responses[index] ? (
                        <div className="response p-2">{responses[index]}</div>
                        ) : null}
            </div>
        ))}
      </div>
      <div className="chat-input pt-2">
      <form
        className="d-flex"
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
            <button className="btn my-button d-flex align-items-center h-10" type="submit">
                <SendIcon className="send-icon"/>
            </button>
        </form>
    </div>
    </div>
  );
}

export default Chat;