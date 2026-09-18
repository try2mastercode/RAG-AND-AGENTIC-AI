import random
import string
from typing import TypedDict
from langgraph.graph import *
class chain_state(TypedDict):
    n:int
    letter:str
initial_state=chain_state(n=1,letter='a')
print(initial_state)

def add(state:chain_state)->chain_state:
    random_letter = random.choice(string.ascii_letters)
    return {**state,"n":state["n"]+1,"letter":random_letter}

def print_out(state:chain_state)->chain_state:
    print("Current n:",state["n"],"Letter:",state["letter"])
    return state
workflow=StateGraph(chain_state)
workflow.add_node("add",add)
workflow.add_node("print",print_out)
workflow.add_edge("add","print")
def stop_condtions(state:chain_state)->bool:
    return state["n"]>=13
workflow.add_conditional_edges("print",stop_condtions,{True:END,False:"add"})
workflow.set_entry_point("add")
app=workflow.compile()
result=app.invoke({"n":1,"letter":""})
print("Final state:",result)