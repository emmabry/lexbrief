import { useState, useEffect } from 'react';

type InfoCardProps = {
    celex: string;
  };  

interface EurlexData {
    title: string;
    text: string;
    related_documents: string[];
  }

function InfoCard({ celex }: InfoCardProps) {
    const [data, setData] = useState<EurlexData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        fetch(`http://localhost:8000/eurlex/${celex}`)
        .then((res) => {
            if (!res.ok) throw new Error(`Error: ${res.status}`);
            return res.json();
        })
        .then((data: EurlexData) => {
            setData(data);
            setLoading(false);
        })
        .catch((err) => {
            setError(err.message);
            setLoading(false);
        });
    }, [celex]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
    <div className="info-card">
      <h2>{data?.title}</h2>
      <p>{data?.text.substring(0, 200)}...</p> 
    </div>
    );
}

export default InfoCard;
