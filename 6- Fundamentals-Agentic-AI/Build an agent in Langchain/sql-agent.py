# ---------- SECTION 1: IMPORTS ----------
import os
import sys
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent


# ---------- SECTION 2: BUILD A SAMPLE SQLITE DATABASE ----------
# A tiny two-table company DB, created fresh each run so the script is
# self-contained and needs no external database server.
db_path = os.path.join(os.path.dirname(__file__), "company.db")
if os.path.exists(db_path):
    os.remove(db_path)

connection = sqlite3.connect(db_path)

departments_df = pd.DataFrame(
    {
        "department_id": [1, 2, 3],
        "department_name": ["Engineering", "Sales", "Marketing"],
    }
)
employees_df = pd.DataFrame(
    {
        "employee_id": [1, 2, 3, 4, 5],
        "name": ["Asha", "Ben", "Chen", "Diya", "Evan"],
        "department_id": [1, 1, 2, 3, 2],
        "salary": [95000, 88000, 72000, 68000, 75000],
    }
)

departments_df.to_sql("departments", connection, index=False)
employees_df.to_sql("employees", connection, index=False)
connection.close()


# ---------- SECTION 3: MODEL (Groq) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",  # allam-2-7b (GROQ_MODEL) has no tool-calling support
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- SECTION 4: CONNECT LANGCHAIN TO THE DATABASE ----------
# SQLDatabase is LangChain's wrapper for reading a DB's schema and running
# queries against it - the agent uses it to see table structure and to
# execute the SQL it writes.
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")


# ---------- SECTION 5: BUILD THE SQL TOOLKIT ----------
# SQLDatabaseToolkit bundles the standard set of tools a SQL agent needs:
# list tables, inspect a table's schema, run a query, and check a query's
# syntax before executing it.
toolkit = SQLDatabaseToolkit(db=db, llm=llm)


# ---------- SECTION 6: ASSEMBLE THE BUILT-IN SQL AGENT ----------
# create_sql_agent wires the LLM + toolkit into LangChain's prebuilt
# SQL-agent loop: the model inspects the schema, writes SQL, runs it via the
# toolkit's tools, and iterates if the query needs correcting.
sql_agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="tool-calling",
    verbose=True,
)


# ---------- SECTION 7: ASK NATURAL-LANGUAGE QUESTIONS ----------
print("=== AI-powered SQL agent ===")
questions = [
    "Which department has the highest total salary?",
    "List employee names and salaries in the Engineering department.",
]

for question in questions:
    print(f"\nQ: {question}")
    response = sql_agent.invoke({"input": question})
    print("A:", response["output"])
