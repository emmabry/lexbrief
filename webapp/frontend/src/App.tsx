import React from 'react';
import { useState } from 'react';
import './App.css';
import InfoCard from './infoCard';
import Summary from './Summary';
import Answer from './Answer';

function App() {
  const [celexInfo, setCelexInfo] = useState<string | null>(null); 
  const [sumloading, setsumLoading] = useState<boolean>(false);
  const [ansloading, setAnsLoading] = useState<boolean>(false);
  const [summary, setSummary] = useState<string | null>(null); 
  const [answer, setAnswer] = useState<string | null>(null);

  const fetchSummary = async () => {
    setsumLoading(true);
    if (!celexInfo) return;
  
    try {
      const res1 = await fetch(`http://localhost:8000/eurlex/${celexInfo}`);
      if (!res1.ok) throw new Error(`Failed to fetch CELEX`);
      const data = await res1.json();
  
      const res2 = await fetch('http://localhost:8000/summarise_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: data.text }),
      });
  
      if (!res2.ok) throw new Error(`Failed to summarise`);
      const summaryData = await res2.json();
      setSummary(summaryData.summary);
      setsumLoading(false);
  
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAnswer = async () => {
    setAnsLoading(true);
    if (!celexInfo) return;

    try {
      const res1 = await fetch(`http://localhost:8000/eurlex/${celexInfo}`);
      if (!res1.ok) throw new Error(`Failed to fetch CELEX`);
      const data = await res1.json();

      const res2 = await fetch('http://localhost:8000/ask_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: data.text,
          question: "What is the aim of this act?" })
         });

         if (!res2.ok) throw new Error(`Failed to ask question`);
         const answerData = await res2.json();
         setAnswer(answerData.answer);
          setAnsLoading(false);
      } catch (err) {
        console.error(err);
      }
    };

  return (
    <div className="App">
      <div className="buttons">
        <button onClick={() => setCelexInfo('32025D0047')}>Get CELEX 32025D0047</button>
        <button onClick={() => fetchSummary()}>Summarise CELEX 32025D0047</button>
        <p>This button asks what is the aim of this act?</p>
        <button onClick={() => fetchAnswer()}>QA CELEX for 32025D0047</button>
      </div>
      <div className="info">
      { celexInfo ? (
        <InfoCard celex={celexInfo} />
      ) : (
        <p>Click a button to get CELEX information.</p>
      )}
    </div>
    <div className="summary">
      { summary ? (
        <Summary summary={summary} />
      ) : sumloading? (
        <p>Loading summary...</p>
      ) : (
        <p>Click a button to ask about the document.</p>
      )}
    </div>
    <div className="qa">
      { answer ? (
        <Answer answer={answer} />
      ) : ansloading? (
        <p>Loading answer...</p>
      ) : (
        <p>Click a button to ask about the document.</p>
      )}
    </div>
  </div>
  );
}

export default App;
