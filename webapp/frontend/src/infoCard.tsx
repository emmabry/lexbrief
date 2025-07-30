type CelexData = {
    title: string;
    text: string;
    related_documents: string[];
  }

function InfoCard( data: CelexData ) {
    return (
    <div className="info-card">
      <h2>{data?.title}</h2>
      <p>{data?.text.substring(0, 200)}...</p> 
    </div>
    );
}

export default InfoCard;
