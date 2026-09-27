import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .config import settings
from .schemas import GeneratedQuiz

SYSTEM = """You generate objective educational multiple-choice quizzes.
Return ONLY valid JSON matching this exact structure:
{{
  "title": "string",
  "topic": "string",
  "questions": [
    {{
      "question": "string",
      "options": ["A option", "B option", "C option", "D option"],
      "correct_answer": "A",
      "explanation": "short explanation"
    }}
  ]
}}
Rules:
- Exactly four unique options per question.
- Exactly one correct answer.
- correct_answer must be A, B, C, or D.
- Questions must be factually answerable.
- Do not include markdown fences.
"""

def generate_quiz(topic: str, title: str, count: int) -> GeneratedQuiz:
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=settings.groq_api_key,
        temperature=0.2,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM),
        ("human", "Create a {count}-question quiz about: {topic}. Title: {title}")
    ])
    response = llm.invoke(prompt.format_messages(
        count=count, topic=topic, title=title
    ))
    raw = response.content
    if isinstance(raw, list):
        raw = "".join(str(x) for x in raw)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    return GeneratedQuiz.model_validate(data)
