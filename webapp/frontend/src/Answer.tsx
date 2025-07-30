type AnswerProps = {
    answer: string;
  };  

function Answer({ answer }: AnswerProps) {

    return (
    <div className="answer-card">
      <p>{answer}</p>
    </div>
    );
}

export default Answer;