from pydantic import BaseModel

class QARequest(BaseModel):
    text: str
    question: str
