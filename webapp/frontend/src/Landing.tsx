import search from './assets/search.svg'; 

type LandingProps = {
    celexId: string;
    setCelexId: React.Dispatch<React.SetStateAction<string>>;
    handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  };

function Landing({ celexId, setCelexId, handleSubmit }: LandingProps) {
    return (
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
          <form className="p-2 d-flex" onSubmit={handleSubmit}>
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
        <p className="small celex-text">Don't know the CELEX number? Search for documents on <a href="https://eur-lex.europa.eu/homepage.html" 
        className="my-link" target="_blank"
        rel="noopener noreferrer">EUR-Lex</a></p>
        </div>
      </div>
    );
}

export default Landing;