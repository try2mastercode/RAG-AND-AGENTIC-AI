import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)


# ---------- SECTION 1: SAMPLE SQLITE DATABASE (built once, on import) ----------
DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")

if not os.path.exists(DB_PATH):
    connection = sqlite3.connect(DB_PATH)
    pd.DataFrame(
        {"department_id": [1, 2, 3], "department_name": ["Engineering", "Sales", "Marketing"]}
    ).to_sql("departments", connection, index=False)
    pd.DataFrame(
        {
            "employee_id": [1, 2, 3, 4, 5],
            "name": ["Asha", "Ben", "Chen", "Diya", "Evan"],
            "department_id": [1, 1, 2, 3, 2],
            "salary": [95000, 88000, 72000, 68000, 75000],
        }
    ).to_sql("employees", connection, index=False)
    connection.close()


# ---------- SECTION 2: WIRE LANGCHAIN TO THE DATABASE ----------
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# create_sql_agent's toolkit already covers what a SQL agent needs: list
# tables, inspect a table's schema, run a query, and check syntax before
# executing it - the agent decides which of these to call and in what order.
sql_agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="tool-calling",
    agent_executor_kwargs={"return_intermediate_steps": True},
)


# ---------- SECTION 3: ASK A NATURAL-LANGUAGE QUESTION ----------
def ask(question: str) -> dict:
    response = sql_agent.invoke({"input": question})
    steps = [
        {"tool": action.tool, "tool_input": action.tool_input, "observation": str(observation)}
        for action, observation in response.get("intermediate_steps", [])
    ]
    return {"answer": response["output"], "steps": steps}
