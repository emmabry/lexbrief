type SummaryProps = {
    summary: string;
  };  

function Summary({ summary }: SummaryProps) {

    return (
    <div className="summary-card">
      <p>{summary}</p>
    </div>
    );
}

export default Summary;