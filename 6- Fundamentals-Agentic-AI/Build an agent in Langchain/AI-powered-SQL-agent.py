# ---------- SECTION 1: IMPORTS ----------
import os
import sys
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent


# ---------- SECTION 2: BUILD A SAMPLE SQLITE DATABASE ----------
# Same two-table company DB as sql-agent.py, so the two scripts are a fair
# apples-to-apples comparison: built-in toolkit vs. hand-written tools.
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


# ---------- SECTION 4: CUSTOM SQL TOOLS ----------
# Unlike sql-agent.py (SQLDatabaseToolkit + create_sql_agent), the model here
# gets three hand-written tools and has to decide when to call each one.
@tool
def list_tables() -> str:
    """List every table name in the database."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return ", ".join(r[0] for r in rows)


@tool
def get_schema(table_name: str) -> str:
    """Return the column names and types for a given table."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    conn.close()
    if not rows:
        return f"No such table: {table_name}"
    return ", ".join(f"{r[1]} ({r[2]})" for r in rows)


@tool
def run_sql_query(query: str) -> str:
    """Run a read-only SQL SELECT query against the database and return the rows."""
    if not query.strip().lower().startswith("select"):
        return "Only SELECT queries are allowed."
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        return f"SQL error: {e}"
    finally:
        conn.close()
    return str(rows)


tools = [list_tables, get_schema, run_sql_query]


# ---------- SECTION 5: BUILD THE AGENT ----------
# A generic create_agent loop (same primitive as tool-fundamentals-and-agents.py)
# instead of the SQL-specific prebuilt agent - it has to inspect the schema
# itself before it can write a correct query.
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a SQL assistant. Before writing a query, call list_tables and "
        "get_schema to learn the table structure. Only run SELECT queries."
    ),
)


# ---------- SECTION 6: ASK NATURAL-LANGUAGE QUESTIONS ----------
print("=== Custom-tools SQL agent ===")
questions = [
    "Which department has the highest total salary?",
    "List employee names and salaries in the Engineering department.",
]

for question in questions:
    print(f"\nQ: {question}")
    result = agent.invoke({"messages": [HumanMessage(question)]})
    print("A:", result["messages"][-1].content)
