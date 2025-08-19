import ChatIcon from '../assets/chat.svg?react';
import PopupIcon from '../assets/popup.svg?react';
import LinkIcon from '../assets/link.svg?react';
import ReactMarkdown from 'react-markdown';


import Chat from './Chat.tsx';

interface RelatedDocItem {
  Relation?: string;
  Act: {
    celex?: string;
    url?: string;
  };
}

type SummaryProps = {
    summaryData: {
      summary: string;
      insights: string[];
    };
    celexData: {
      title: string;
      text: string;
      related_documents: {
        modifies: RelatedDocItem[];
        modified_by: RelatedDocItem[];
      };
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
              {(
  (celexData?.related_documents?.modifies?.length ?? 0) > 0 ||
  (celexData?.related_documents?.modified_by?.length ?? 0) > 0
) && (
  <div className="border-top">
    {(celexData?.related_documents?.modifies?.length ?? 0) > 0 && (
      <div>
        <h6 className="mt-4"> <LinkIcon className="link-icon"/>Acts affected by this legislation</h6>
          {celexData?.related_documents.modifies.map((item, idx) => (
            <div key={idx} className="border reference-box p-2 rounded-3 mb-2">
              <div className="d-flex">
                <p className="rounded-5 border small fw-semibold px-2 mb-0 me-2">{item.Act.celex}</p>
                <p className="rounded-5 modifies small fw-semibold px-2 mb-0">Repealed</p>
              </div>
              <a href={item.Act.url} target="_blank" rel="noopener noreferrer" aria-label={`Open ${item.Act.celex} in a new tab`} className="mb-0"><PopupIcon className="link-icon"/></a>
            </div>
          ))}
      </div>
    )}

    {(celexData?.related_documents?.modified_by?.length ?? 0) > 0 && (
      <div>
        <h6 className="mt-4"> <LinkIcon className="link-icon"/>Acts that affect this legislation</h6>
          {celexData?.related_documents.modified_by.map((item, idx) => (
           <div key={idx} className="border reference-box p-2 rounded-3 mb-2">
           <div className="d-flex">
             <p className="rounded-5 border small fw-semibold px-2 mb-0 me-2">{item.Act.celex}</p>
             <p className="rounded-5 modified small fw-semibold px-2 mb-0">Modifies this act</p>
           </div>
             <a href={item.Act.url} target="_blank" rel="noopener noreferrer" aria-label={`Open ${item.Act.celex} in a new tab`} className="mb-0"><PopupIcon className="link-icon"/></a>
         </div>
            ))}
      </div>
    )}
  </div>
)}
          </div>
        <div className="summary-l-card p-4 border m-3 rounded-3">
          <div>
          <h4>Generated Summary</h4>
          <p className="summary-text"><ReactMarkdown>{summaryData.summary}</ReactMarkdown></p>
          </div>
          <div>
            <h4>Key Insights</h4>
            {summaryData.insights.map((sentence, i) => (
              <p key={i} className="summary-text"><ReactMarkdown>{`${sentence}.`}</ReactMarkdown></p> ))}
          </div>
        </div>
      </div>
      <div className="m-4" style={{ width: '35%' }}>
        <div className="summary-l-card border p-4 m-3 chat-container rounded-3">
          <div className="d-flex align-items-center">
            <ChatIcon className="chat-icon" />
            <h4 className="fw-semibold">AI Assistant</h4>
          </div>
            {summaryData && celexData && <Chat celexData={{ title: celexData.title, text: celexData.text }} />}
          </div>
        </div>
      </div>
    );
}

export default Summary; 