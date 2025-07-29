import React from 'react';
import { useState } from 'react';
import './App.css';
import InfoCard from './infoCard';

function App() {
  const [celexInfo, setCelexInfo] = useState<string | null>(null); 
  return (
    <div className="App">
      <div className="buttons">
        <button onClick={() => setCelexInfo('32025D0047')}>Get CELEX 32025D0047</button>
        <button>Summarise CELEX 32025D0047</button>
        <p>This button asks what is the aim of this act?</p>
        <button>QA CELEX for 32025D0047</button>
      </div>
      <div className="output">
      { celexInfo ? (
        <InfoCard celex={celexInfo} />
      ) : (
        <p>Click a button to get CELEX information.</p>
      )}
    </div>
  </div>
  );
}

export default App;
