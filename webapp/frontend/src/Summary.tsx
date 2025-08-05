import ChatIcon from './assets/chat.svg?react';
import PopupIcon from './assets/popup.svg?react';
import { useState } from 'react';
import Chat from './Chat.tsx';

type SummaryProps = {
    summary: string;
    celexData: {
      title: string;
      text: string;
      related_documents: string[];
    } | null;
  };  

function Summary({ summary, celexData }: SummaryProps) {
  const [showChat, setShowChat] = useState(false);

    return (
      <div className='d-flex flex-row align-items-start px-5 w-100'>
        <div className="m-4" style={{ width: '60%' }}>
          <div className="summary-l-card border p-4 m-3 rounded-3">
            <h5>{celexData?.title}</h5>
            <p className="text-muted">Published: 14 December 2024</p>
            <button className="btn my-button mt-3 w-100 d-flex justify-content-center align-items-center">
              <PopupIcon className="button-icon" />
              View Full Text</button>
          </div>
        <div className="summary-l-card p-4 border m-3 rounded-3">
          <h4>Generated Summary</h4>
          <p className="summary-text">{summary}</p>
        </div>
      </div>
      <div className="m-4" style={{ width: '35%' }}>
        <div className="summary-l-card border p-4 m-3 rounded-3">
          <div className="d-flex align-items-center">
            <ChatIcon className="chat-icon" />
            <h4>AI Assistant</h4>
          </div>
          { !showChat ? (
            <div>
          <p className="text-muted">Have questions about this document? Chat with our AI assistant for detailed explanations.</p>
            <button type="submit" className="btn my-button w-100" onClick={() => setShowChat(true)}>
              Open chat</button>
            </div>
          ) : (
          <div className="chat-opened">
            {summary && celexData && <Chat celexData={celexData} />}
            <button type="button" className="btn my-button w-100" onClick={() => setShowChat(false)}>
              Close chat</button>
          </div>
          )}
        </div>
      </div>
    </div>
    );
}

export default Summary; 