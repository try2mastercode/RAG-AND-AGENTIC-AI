# ---------- SECTION 1: IMPORTS ----------
# TODO: os, dotenv's load_dotenv, sys
# TODO: pandas (to build the sample tables)
# TODO: from sqlalchemy import create_engine   (needed to talk to MySQL, unlike sqlite3)
# TODO: from langchain_groq import ChatGroq   (same LLM used elsewhere in this repo)
# TODO: from langchain_community.utilities import SQLDatabase
# TODO: from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# TODO: from langchain_community.agent_toolkits.sql.base import create_sql_agent


# ---------- SECTION 2: MODEL (Groq) ----------
# TODO: load_dotenv()
# TODO: llm = ChatGroq(model="qwen/qwen3.8-27b", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
#       - same model as sql-agent.py, for the same reason: the .env default GROQ_MODEL has no
#         tool-calling support, and the agent needs that to work


# ---------- SECTION 3: BUILD A SIMPLE SAMPLE DATABASE ON YOUR MYSQL SERVER ----------
# Keep this small - a couple of artists, a handful of albums - just enough to prove the agent can
# count/filter/join, without needing to import the full Chinook dataset.
# TODO: read MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE from .env
# TODO: build the connection URL: "mysql+mysqlconnector://<user>:<password>@<host>/<database>"
# TODO: engine = create_engine(<that URL>)
# TODO: artists_df = a small DataFrame: artist_id, artist_name (e.g. 3 rows)
# TODO: albums_df = a small DataFrame: album_id, title, artist_id (e.g. 6 rows, referencing artists_df)
# TODO: artists_df.to_sql("artists", engine, if_exists="replace", index=False)
# TODO: albums_df.to_sql("albums", engine, if_exists="replace", index=False)


# ---------- SECTION 4: CONNECT LANGCHAIN TO THE DATABASE ----------
# TODO: db = SQLDatabase.from_uri(<the same MySQL URL from Section 3>)


# ---------- SECTION 5: BUILD THE SQL TOOLKIT ----------
# TODO: toolkit = SQLDatabaseToolkit(db=db, llm=llm)


# ---------- SECTION 6: ASSEMBLE THE SQL AGENT ----------
# TODO: sql_agent = create_sql_agent(llm=llm, toolkit=toolkit, agent_type="tool-calling", verbose=True)
#       - verbose=True prints the full reasoning trace: which tables it inspected, the SQL it wrote,
#         and the query result - not just the final answer


# ---------- SECTION 7: TEST THE AGENT ----------
# TODO: sql_agent.invoke({"input": "How many albums are listed in the database?"})
# Expected result: however many rows you put in albums_df in Section 3 (e.g. 6) - the point is that
# it should match exactly what "SELECT COUNT(*) FROM albums;" would return directly.
