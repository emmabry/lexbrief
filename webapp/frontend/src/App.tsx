import { useState } from 'react';
import './App.css';
import Summary from './Summary.tsx';
import Landing from './Landing.tsx';
import Loading from './Loading.tsx';
import logo from './assets/artificial-intelligence.png'; 

type CelexData = {
  title: string;
  text: string;
  related_documents: string[];
};

function App() {
  const [celexData, setCelexData] = useState<CelexData | null>(null); 
  const [celexId, setCelexId] = useState<string>('');
  const [sumLoading, setsumLoading] = useState<boolean>(false);
  const [dataLoading, setDataLoading] = useState<boolean>(false);
  const [page, setPage] = useState<'landing' | 'info' | 'summary' | 'chat'>('landing');
  const [summary, setSummary] = useState<string | null>(null); 

  const fetchCelexData = async (celex: string): Promise<CelexData | null> => {
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

  const fetchSummary = async (data: CelexData) => {
    console.log(`Fetching summary for CELEX: ${data?.title}`);
    if (!data) return;
    try {
      const res = await fetch('http://localhost:8000/summarise_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: data.text }),
      });
  
      if (!res.ok) throw new Error(`Failed to summarise`);
      const summaryData = await res.json();
      setSummary(summaryData.summary);
      setsumLoading(false);
    } catch (err) {
      console.error(err);
    }
  };

const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setPage('summary');
  setDataLoading(true);
  const data = await fetchCelexData(celexId);
  setCelexData(data);
  setDataLoading(false);
  setsumLoading(true);
  if (!data) {
    setsumLoading(false);
    return console.error('No data found for the provided CELEX ID'); 
  }
  fetchSummary(data);;
};


  return (
    <div className="App">
    <header className="d-flex justify-content-start align-items-center p-3 mb-4"> 
      <img src={logo} width={40} height={40} className="logo" alt="EUR-LEX Logo" />
      <h3 className="mb-1 ms-2 fs-4 fw-bold header-text">LexBrief</h3>
    </header>
      { page === 'landing' ? (
        <Landing
          celexId={celexId}
          setCelexId={setCelexId}
          handleSubmit={handleSubmit}
        />
      ) : page === 'summary' ? ( 
        summary ? (
        <div className ="summary-card">
          <Summary summary={summary} celexData={celexData} celexId={celexId} />
        </div>
        ) : (dataLoading || sumLoading) ? (
          <Loading dataLoading={dataLoading} sumLoading={sumLoading} celexData={celexData} />
        ) : (
        <h1>Error</h1>
      )) : <p>DEBUGGING</p>}
  </div>
  );
}

export default App;
