# AI Quiz Generator & Assessment Platform

A career-aligned GenAI backend project using FastAPI, LangChain, Groq, Pydantic, PostgreSQL, SQLAlchemy and Streamlit.

## Features

- Generate MCQ quizzes with an LLM
- Pydantic validation of AI output
- Store quizzes/questions in PostgreSQL
- Generate unique public quiz IDs
- Share a quiz through a URL
- Submit answers through FastAPI
- Server-side answer validation and scoring
- Store attempts and answers
- Streamlit UI
- Docker Compose setup

## 1. Local setup with uv

Install uv first.

Backend:

```bash
cd backend
uv init
uv add -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/quiz_generator
GROQ_API_KEY=your_key
```

Run:

```bash
uv run uvicorn app.main:app --reload
```

Frontend in another terminal:

```bash
cd frontend
uv init
uv add -r requirements.txt
copy .env.example .env
uv run streamlit run app.py
```

Open the Streamlit URL shown in the terminal.

## 2. PostgreSQL

Create:

```text
Database: quiz_generator
User: postgres
Password: your password
```

The application creates its tables automatically when the backend starts.

## 3. Docker

Create a root `.env`:

```env
GROQ_API_KEY=your_key
```

Then:

```bash
docker compose up --build
```

Frontend: http://localhost:8501

Backend docs: http://localhost:8000/docs

## 4. Shareable quiz link

Create a quiz in Streamlit.

You receive a public quiz ID such as:

```text
AbC123xyz
```

Your deployed frontend link becomes:

```text
https://YOUR-FRONTEND-DOMAIN/?quiz=AbC123xyz
```

Send that link to the student.

## Architecture

Student -> Streamlit -> FastAPI -> PostgreSQL

Quiz creation:

User -> Streamlit -> FastAPI -> LangChain -> Groq -> Pydantic validation -> PostgreSQL

Quiz submission:

Student -> Streamlit -> FastAPI -> server-side validation -> score -> PostgreSQL

## Validation

The project validates:

1. Quiz request fields with Pydantic.
2. AI output structure with Pydantic.
3. Exactly four unique options.
4. Correct answer is A/B/C/D.
5. Quiz ID exists.
6. Every question is answered exactly once.
7. Question IDs belong to the selected quiz.
8. Submitted answers are compared with server-side correct answers.

## Important deployment note

For a public production deployment, use managed PostgreSQL and HTTPS. Put the Groq API key only in backend environment variables; never expose it in Streamlit code.

## Future upgrades

- PDF upload and PyMuPDF extraction
- RAG-based quiz generation from uploaded documents
- Login/authentication
- Admin dashboard
- Timer enforcement
- Result analytics
- Difficulty levels
- Question review/editing
- Redis/rate limiting
- LangGraph workflow for question generation + verification
