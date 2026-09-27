from pydantic import BaseModel, Field, field_validator

class GeneratedQuestion(BaseModel):
    question: str = Field(min_length=5)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str = Field(min_length=3)

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(cls, value):
        if value.upper() not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer must be A, B, C or D")
        return value.upper()

    @field_validator("options")
    @classmethod
    def validate_options(cls, value):
        if len(set(x.strip().lower() for x in value)) != 4:
            raise ValueError("Options must be unique")
        return value

class GeneratedQuiz(BaseModel):
    title: str
    topic: str
    questions: list[GeneratedQuestion] = Field(min_length=1, max_length=20)

class CreateQuizRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    topic: str = Field(min_length=2, max_length=200)
    number_of_questions: int = Field(default=10, ge=1, le=20)

class QuestionOut(BaseModel):
    id: int
    question: str
    options: dict[str, str]

class QuizOut(BaseModel):
    public_id: str
    title: str
    topic: str
    questions: list[QuestionOut]

class AnswerInput(BaseModel):
    question_id: int
    selected_answer: str

    @field_validator("selected_answer")
    @classmethod
    def validate_selected(cls, value):
        value = value.upper()
        if value not in {"A", "B", "C", "D"}:
            raise ValueError("Answer must be A, B, C or D")
        return value

class SubmitQuizRequest(BaseModel):
    student_name: str = Field(min_length=1, max_length=120)
    answers: list[AnswerInput]

class ResultOut(BaseModel):
    student_name: str
    score: int
    total_questions: int
    percentage: float
