from pydantic import BaseModel

class QARequest(BaseModel):
    text: str
    question: str

class SumRequest(BaseModel):
    text: str