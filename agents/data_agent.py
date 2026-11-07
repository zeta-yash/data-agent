import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from models.schema import RouterSchema,DataAgentSchema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from agents.etl_analyst import etl_analyst
from agents.sql_analyst import sql_analyst


llm = pick_llm("medium")

llm_router = llm.with_structured_output(RouterSchema)



#-------------- DATA AGENT GRAPH----------------------------

def router_node(state:DataAgentSchema):
    message = state.messages[-1].content
    print(f"\n[DataAgent] Routing query: {message[:80]}...")

    prompt = f"""You are an expert request router. Classify the user query into either 'sql' or 'etl':
- 'sql': For queries asking questions about existing database records, SQL tables, querying PostgreSQL, running queries, or reporting on database data.
- 'etl': For queries involving extracting data from APIs/URLs, downloading data, transforming files (CSV, JSON, Parquet), filtering file data, or saving files to folders.

User Query: {message}"""

    route_response_dict = llm_router.invoke(prompt).model_dump()
    route_response = route_response_dict['answer'].lower().strip()
    print(f"[DataAgent] Route selected: {route_response.upper()}")

    return {"route_response": route_response}  # #ai-help - return dict to avoid duplicating messages

def etl_node(state:DataAgentSchema):
    message = state.messages[-1].content
    print("[DataAgent] Dispatching to ETL Analyst...")

    response = etl_analyst.invoke(
        {"messages": [HumanMessage(content=f"{message}")]}
    )
    final_msg = AIMessage(content=response['messages'][-1].content)
    print("[DataAgent] ETL Analyst completed.")

    return {"messages": [final_msg]}  # #ai-help - return delta so add reducer appends cleanly

def sql_node(state:DataAgentSchema):

    message = state.messages[-1].content
    print("[DataAgent] Dispatching to SQL Analyst...")

    input_schema = {
        "messages": [],
        "user_question": f"{message}",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }

    response = sql_analyst.invoke(input_schema)

    final_msg = AIMessage(content=response['final_answer'])
    print("[DataAgent] SQL Analyst completed.")

    return {"messages": [final_msg]}  # #ai-help - return delta so add reducer appends cleanly

data_agent_graph = StateGraph(DataAgentSchema)

data_agent_graph.add_node("router_node",router_node)
data_agent_graph.add_node("etl_node", etl_node)
data_agent_graph.add_node("sql_node", sql_node)

data_agent_graph.add_edge(START, "router_node")
def route_edge(state:DataAgentSchema):
    if state.route_response == "sql":
        return "sql_node"
    elif state.route_response == "etl":
        return "etl_node"
    else:
        raise ValueError(f"Invalid route response: {state.route_response}")

data_agent_graph.add_conditional_edges( "router_node",route_edge,
    {
        "sql_node":"sql_node",
        "etl_node":"etl_node"
    }
)



data_agent_graph.add_edge("etl_node", END)  # Bug 4 fix: terminal nodes need edges to END
data_agent_graph.add_edge("sql_node", END)  # Bug 4 fix

data_agent = data_agent_graph.compile()  # Bug 5 fix: typo "complie" → "compile"

# Optional — only run graph visualisation in interactive/notebook environments
# from IPython.display import display, Image
# img = Image(data_agent.get_graph().draw_mermaid_png())
# with open("data_agent_graph.png", "wb") as f:
#     f.write(img.data)
if __name__ == "__main__":
    response = data_agent.invoke(
        {"messages":[HumanMessage(content="I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in the csv folder")],
         "route_response": ""}
    )

    print(response)