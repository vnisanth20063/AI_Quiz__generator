# Architecture

```text
                    +-------------------+
                    |     Student       |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    |    Streamlit UI   |
                    +---------+---------+
                              |
                         HTTP / JSON
                              |
                              v
                    +-------------------+
                    |     FastAPI       |
                    +----+---------+----+
                         |         |
                    SQLAlchemy      | LangChain
                         |         |
                         v         v
                  +-----------+  +------+
                  | PostgreSQL|  | Groq |
                  +-----------+  +------+

Quiz creation:
Streamlit -> FastAPI -> LangChain/Groq -> Pydantic validation -> PostgreSQL

Quiz taking:
Public URL -> Streamlit -> FastAPI -> PostgreSQL -> questions

Submission:
Student answers -> FastAPI -> server-side validation -> score -> PostgreSQL
