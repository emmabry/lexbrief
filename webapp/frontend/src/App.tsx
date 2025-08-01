import React from 'react';
import { useState } from 'react';
import './App.css';
import logo from './assets/artificial-intelligence.png'; 
import search from './assets/search.svg'; 
import Summary from './Summary';
import Answer from './Answer';
import InfoCard from './infoCard';

type CelexData = {
  title: string;
  text: string;
  related_documents: string[];
};

function App() {
  const [celexData, setCelexData] = useState<CelexData | null>(null); 
  const [celexId, setCelexId] = useState<string>('');
  const [dataLoading, setDataLoading] = useState<boolean>(false);
  const [sumloading, setsumLoading] = useState<boolean>(false);
  const [ansloading, setAnsLoading] = useState<boolean>(false);
  const [page, setPage] = useState<'landing' | 'info' | 'summary' | 'chat'>('landing');
  const [summary, setSummary] = useState<string | null>(null); 
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string | null>(null);

  const fetchCelexData = async (celex: string): Promise<CelexData | null> => {
    setDataLoading(true);
    console.log(`Fetching CELEX data for: ${celex}`);
    try {
      const response = await fetch(`http://localhost:8000/eurlex/${celex}`);
      if (!response.ok) throw new Error(`Failed to fetch CELEX data`);
      const data = await response.json();
      return {
        title: data.title,
        text: data.text,
        related_documents: data.related_documents || [],
      };
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  const fetchSummary = async () => {
    console.log(`Fetching summary for CELEX: ${celexData?.title}`);
    setPage('summary');
    setsumLoading(true);
    if (!celexData) return;
  
    try {
      const res = await fetch('http://localhost:8000/summarise_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: celexData.text }),
      });
  
      if (!res.ok) throw new Error(`Failed to summarise`);
      const summaryData = await res.json();
      setSummary(summaryData.summary);
      setsumLoading(false);
  
    } catch (err) {
      console.error(err);
    }
  };
  
  const fetchAnswer = async (q: string) => {
    console.log(`Fetching answer for question: ${q} on CELEX: ${celexData?.title}`);
    setPage('chat');
    setAnsLoading(true);
    if (!celexData) return;

    try {
      const res = await fetch('http://localhost:8000/ask_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: celexData.text,
          question: q })
         });

         if (!res.ok) throw new Error(`Failed to ask question`);
         const answerData = await res.json();
          setPage('chat');
          setAnswer(answerData.answer);
          setAnsLoading(false);
      } catch (err) {
        console.error(err);
      }
    };

  return (
    <div className="App">
    <header className="d-flex justify-content-start align-items-center p-3 mb-4"> 
      <img src={logo} width={40} height={40} className="logo" alt="EUR-LEX Logo" />
      <h3 className="mb-1 ms-2 fs-4 fw-bold header-text">LexBrief</h3>
    </header>
      { page === 'landing' ? (
      <div className="main-card px-4 pt-5 my-5 text-center mx-auto d-flex flex-column align-items-center w-75">
        <div className="pass w-75 mx-0">
        <h1 className="display-4 fw-bold text-body-emphasis mb-0">AI-Powered EU Policy</h1>
        <h1 className="landing-title display-4 fw-bold text-body-emphasis mt-0"> Document Analysis</h1>
        <p className="hero-text fs-5 fw-medium mx-auto my-4 w-75">Get instant, intelligent summaries of EU legal documents using CELEX numbers. 
          Streamline your policy research with advanced AI analysis.</p>
        </div>
        <div className="celex-form mx-auto m-4 p-3 w-75 rounded-3 shadow-sm" style={{ maxWidth: '68%' }}>
          <h4 className="celex-header">Enter CELEX Number</h4>
          <p className="celex-text">Input any EU legal document identifier to generate an AI summary</p>
        <form className="p-2 d-flex" onSubmit={async (e) => {
          setPage('info');
          e.preventDefault();
          setDataLoading(true);
          const data = await fetchCelexData(celexId);
          setCelexData(data);
          setDataLoading(false);
        }}>
          <input
          className="form-control me-2 flex-grow-1"
          type="text"
          placeholder="e.g., 32025D1267"
          value={celexId}
          onChange={(e) => {
            setCelexId(e.target.value);
            }}
          />
          <button className="btn my-button d-flex align-items-center h-10 px-4 py-2" type="submit">
            <img src={search} alt="Search icon" className="icon-white me-2" />
            Summarise
          </button>
        </form>
        <p className="small celex-text">Don't know the CELEX number? Search for documents on <a href="google.com" className="my-link">EUR-Lex</a></p>
        </div>
      </div>
      ) : page === 'info' ? (
        celexData ? (
          <div className="info-card">
            <InfoCard {...celexData} />
            <button onClick={() => {
              fetchSummary();
            }}>Summarise</button>
          </div>
      ) : dataLoading ? (
          <p>Loading CELEX data...</p>
        ) : (
          <h1>Error: placeholder</h1>
        )
      ) : page === 'summary' ? ( 
        summary ? (
        <div className ="summary-card">
          <Summary summary={summary} />
          <form onSubmit={(e) => {
            fetchAnswer(question);
            e.preventDefault();
          }}>
            <input
              type="text"
              placeholder="Enter your question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <button type="submit">Submit</button>
          </form>
        </div>
        ) : sumloading? (
          <p>Loading summary...</p>
        ) : (
        <h1>Error</h1>
      )) : page === 'chat' ? (
        answer ? (
          <div className="answer-card">
            <Answer answer={answer} />
            <form onSubmit={(e) => {
              fetchAnswer(question);
              e.preventDefault();
            }}>
              <input
                type="text"
                placeholder="Ask another question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
              <button type="submit">Submit</button>
            </form>
          </div>
        ) : ansloading ? (
          <p>Loading answer...</p>
        ) : (
          <h1>Error</h1>
        )
      ) : <p>DEBUGGING</p>}
  </div>
  );
}

export default App;
