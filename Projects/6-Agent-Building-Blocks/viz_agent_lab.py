import base64
import os

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # render to file, no display window needed
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain.agents import create_agent

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)

CHART_PATH = os.path.join(os.path.dirname(__file__), "output_chart.png")


# ---------- SECTION 1: SAMPLE DATASET ----------
sales_df = pd.DataFrame(
    {
        "region": ["North", "South", "East", "West", "North", "South", "East", "West"],
        "month": ["Jan", "Jan", "Jan", "Jan", "Feb", "Feb", "Feb", "Feb"],
        "revenue": [12000, 9500, 14200, 8700, 13100, 9900, 15300, 9100],
        "units_sold": [120, 95, 142, 87, 131, 99, 153, 91],
    }
)


# ---------- SECTION 2: TOOLS - LET THE AGENT SEE, THEN DRAW ----------
@tool
def describe_dataset() -> str:
    """Return the column names, data types, and a sample of the dataset."""
    return f"Columns: {list(sales_df.columns)}\nSample rows:\n{sales_df.head().to_string()}"


@tool
def create_chart(chart_type: str, x_column: str, y_column: str, title: str) -> str:
    """
    Create a chart from the sales dataset and save it as a PNG file.

    chart_type: one of 'bar', 'line', or 'pie'.
    x_column: column to group by on the x-axis (e.g. 'region', 'month').
    y_column: numeric column to aggregate and plot (e.g. 'revenue', 'units_sold').
    title: chart title.
    """
    grouped = sales_df.groupby(x_column)[y_column].sum()

    fig, ax = plt.subplots(figsize=(6, 4))
    if chart_type == "bar":
        grouped.plot(kind="bar", ax=ax, color="#4C72B0")
    elif chart_type == "line":
        grouped.plot(kind="line", ax=ax, marker="o", color="#4C72B0")
    elif chart_type == "pie":
        grouped.plot(kind="pie", ax=ax, autopct="%1.1f%%")
    else:
        return f"Unsupported chart_type '{chart_type}'. Use 'bar', 'line', or 'pie'."

    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(CHART_PATH)
    plt.close(fig)

    return f"Chart saved to {CHART_PATH}"


TOOLS = [describe_dataset, create_chart]

agent = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=(
        "You are a data visualization assistant. Given a natural-language "
        "request, first call describe_dataset if you're unsure what columns "
        "exist, then call create_chart with the chart type and columns that "
        "best answer the request. Explain what the chart shows in your reply."
    ),
)


# ---------- SECTION 3: RUN A REQUEST, RETURN THE CHART INLINE ----------
def ask(request_text: str) -> dict:
    if os.path.exists(CHART_PATH):
        os.remove(CHART_PATH)

    result = agent.invoke({"messages": [HumanMessage(request_text)]})

    steps = []
    for msg in result["messages"][1:]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            steps.append({"role": "agent", "tool_calls": [
                {"tool": c["name"], "args": c["args"]} for c in msg.tool_calls
            ]})
        elif isinstance(msg, ToolMessage):
            steps.append({"role": "tool", "name": msg.name, "result": msg.content})

    chart_base64 = None
    if os.path.exists(CHART_PATH):
        with open(CHART_PATH, "rb") as f:
            chart_base64 = base64.b64encode(f.read()).decode("ascii")

    return {"reply": result["messages"][-1].content, "steps": steps, "chart_base64": chart_base64}
