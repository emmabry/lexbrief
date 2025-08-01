type AnswerProps = {
    answer: string;
  };  

function Test({ answer }: AnswerProps) {

    return (
    <div className="answer-card">
      <p>{answer}</p>
    </div>
    );
}


export default Test;