import ChatIcon from './assets/chat.svg?react';
import PopupIcon from './assets/popup.svg?react';

import Chat from './Chat.tsx';

type SummaryProps = {
    summaryData: {
      summary: string;
      insights: string[];
    };
    celexData: {
      title: string;
      text: string;
      related_documents: string[];
    } | null;
    celexId?: string;
  };  

function Summary({ summaryData, celexData, celexId }: SummaryProps) {

    return (
      <div className='d-flex flex-row align-items-start px-5 w-100'>
        <div className="m-4" style={{ width: '60%' }}>
          <div className="summary-l-card border p-4 m-3 rounded-3">
            <h5>{celexData?.title}</h5>
            <p className="text-muted">Published: 14 December 2024</p>
            <button className="btn my-button mt-3 w-100 d-flex justify-content-center align-items-center"
            onClick={() => window.open(`https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A${celexId}&qid=1754333530919#PP4Contents`, '_blank')}>
              <PopupIcon className="button-icon" />
              View Full Text</button>
          </div>
        <div className="summary-l-card p-4 border m-3 rounded-3">
          <div>
          <h4>Generated Summary</h4>
          <p className="summary-text">{summaryData.summary}</p>
          </div>
          <div>
            <h4>Key Insights</h4>
            {summaryData.insights.map((sentence, i) => (
              <p key={i} className="summary-text">{sentence}.</p> ))}
          </div>
        </div>
      </div>
      <div className="m-4" style={{ width: '35%' }}>
        <div className="summary-l-card border p-4 m-3 chat-container rounded-3">
          <div className="d-flex align-items-center">
            <ChatIcon className="chat-icon" />
            <h4 className="fw-semibold">AI Assistant</h4>
          </div>
            {summaryData && celexData && <Chat celexData={celexData} />}
          </div>
        </div>
      </div>
    );
}

export default Summary; 