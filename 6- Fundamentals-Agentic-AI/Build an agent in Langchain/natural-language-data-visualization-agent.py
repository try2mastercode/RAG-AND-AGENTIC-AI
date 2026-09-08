# ---------- SECTION 1: IMPORTS ----------
import os
import sys
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # render to file, no display window needed
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent


# ---------- SECTION 2: SAMPLE DATASET ----------
# A small in-memory sales dataset, so the script runs standalone with no
# external file or database needed.
sales_df = pd.DataFrame(
    {
        "region": ["North", "South", "East", "West", "North", "South", "East", "West"],
        "month": ["Jan", "Jan", "Jan", "Jan", "Feb", "Feb", "Feb", "Feb"],
        "revenue": [12000, 9500, 14200, 8700, 13100, 9900, 15300, 9100],
        "units_sold": [120, 95, 142, 87, 131, 99, 153, 91],
    }
)


# ---------- SECTION 3: MODEL (Groq) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",  # allam-2-7b (GROQ_MODEL) has no tool-calling support
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- SECTION 4: TOOL - LET THE AGENT SEE THE DATA IT HAS ----------
# The agent can't pick sensible columns/chart types without knowing what's
# available, so this tool exposes the dataset's shape before any plotting.
@tool
def describe_dataset() -> str:
    """Return the column names, data types, and a sample of the dataset."""
    return f"Columns: {list(sales_df.columns)}\nSample rows:\n{sales_df.head().to_string()}"


# ---------- SECTION 5: TOOL - THE ACTUAL CHART-DRAWING LOGIC ----------
# This is the only tool that touches matplotlib. The agent decides *what*
# to plot (chart type, columns, grouping) from the user's natural-language
# request; this tool just executes that decision.
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

    output_path = os.path.join(os.path.dirname(__file__), "output_chart.png")
    fig.savefig(output_path)
    plt.close(fig)

    return f"Chart saved to {output_path}"


tools = [describe_dataset, create_chart]


# ---------- SECTION 6: ASSEMBLE THE DATA-VISUALIZATION AGENT ----------
# This is a custom agent (not one of LangChain's prebuilt toolkits): the
# tools and system prompt here are purpose-built for turning a natural-
# language request into the right chart.
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a data visualization assistant. Given a natural-language "
        "request, first call describe_dataset if you're unsure what columns "
        "exist, then call create_chart with the chart type and columns that "
        "best answer the request. Explain what the chart shows in your reply."
    ),
)


# ---------- SECTION 7: RUN IT WITH A NATURAL-LANGUAGE REQUEST ----------
print("=== Natural language -> data visualization ===")
result = agent.invoke(
    {
        "messages": [
            HumanMessage("Show me a bar chart comparing total revenue across regions.")
        ]
    }
)

for msg in result["messages"]:
    msg.pretty_print()
