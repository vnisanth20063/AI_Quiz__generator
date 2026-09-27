import secrets
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import Base, engine, get_db
from .models import Quiz, Question, QuizAttempt, Answer
from .schemas import (
    CreateQuizRequest, QuizOut, QuestionOut,
    SubmitQuizRequest, ResultOut
)
from .ai import generate_quiz

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Quiz Generator API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/quizzes")
def create_quiz(payload: CreateQuizRequest, db: Session = Depends(get_db)):
    try:
        generated = generate_quiz(
            payload.topic, payload.title, payload.number_of_questions
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Quiz generation failed: {exc}")

    public_id = secrets.token_urlsafe(8)
    quiz = Quiz(
        public_id=public_id,
        title=generated.title,
        topic=generated.topic
    )
    db.add(quiz)
    db.flush()

    for item in generated.questions:
        q = Question(
            quiz_id=quiz.id,
            question=item.question,
            option_a=item.options[0],
            option_b=item.options[1],
            option_c=item.options[2],
            option_d=item.options[3],
            correct_answer=item.correct_answer,
            explanation=item.explanation,
        )
        db.add(q)

    db.commit()
    return {"public_id": public_id, "message": "Quiz created"}

@app.get("/quizzes/{public_id}", response_model=QuizOut)
def get_quiz(public_id: str, db: Session = Depends(get_db)):
    quiz = db.scalar(select(Quiz).where(Quiz.public_id == public_id))
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = []
    for q in quiz.questions:
        questions.append(QuestionOut(
            id=q.id,
            question=q.question,
            options={
                "A": q.option_a, "B": q.option_b,
                "C": q.option_c, "D": q.option_d
            }
        ))
    return QuizOut(
        public_id=quiz.public_id,
        title=quiz.title,
        topic=quiz.topic,
        questions=questions
    )

@app.post("/quizzes/{public_id}/submit", response_model=ResultOut)
def submit_quiz(
    public_id: str,
    payload: SubmitQuizRequest,
    db: Session = Depends(get_db)
):
    quiz = db.scalar(select(Quiz).where(Quiz.public_id == public_id))
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    question_map = {q.id: q for q in quiz.questions}
    if len(payload.answers) != len(question_map):
        raise HTTPException(
            status_code=400,
            detail="You must submit exactly one answer for every question"
        )

    submitted_ids = [a.question_id for a in payload.answers]
    if len(set(submitted_ids)) != len(submitted_ids):
        raise HTTPException(status_code=400, detail="Duplicate question answers")

    score = 0
    attempt = QuizAttempt(
        quiz_id=quiz.id,
        student_name=payload.student_name,
        score=0,
        total_questions=len(question_map)
    )
    db.add(attempt)
    db.flush()

    for item in payload.answers:
        q = question_map.get(item.question_id)
        if q is None:
            raise HTTPException(status_code=400, detail="Invalid question ID")
        selected = item.selected_answer.upper()
        correct = selected == q.correct_answer
        score += int(correct)
        db.add(Answer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_answer=selected,
            is_correct=correct
        ))

    attempt.score = score
    db.commit()

    percentage = round((score / len(question_map)) * 100, 2)
    return ResultOut(
        student_name=payload.student_name,
        score=score,
        total_questions=len(question_map),
        percentage=percentage
    )
