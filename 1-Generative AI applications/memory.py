import pandas as pd
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

history = InMemoryChatMessageHistory()
history.add_ai_message('hi')
history.add_user_message("what is the capital of france")

df = pd.read_csv("example.csv")
agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    allow_dangerous_code=True,
    return_intermediate_steps=True
)
agent.invoke("how many rows in the dataframe")
