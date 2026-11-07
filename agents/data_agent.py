import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from models.schema import RouterSchema,DataAgentSchema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from etl_analyst import etl_analyst

llm = pick_llm("medium")

llm_router = llm.with_structured_output(RouterSchema)

print(llm_router.invoke("I want to extract data from the API and load it into the destination folder as CSV file."))

#-------------- DATA AGENT GRAPH----------------------------

def router_node(state:DataAgentSchema):
    message = state.messages[-1].content

    route_response_dict = llm_router.invoke(message).model_dump()
    route_response = route_response_dict['answer']
    state.route_response = route_response

def etl_node(state:DataAgentSchema):
    message = state.messages[-1].content
    response = etl_analyst.invoke(
             {"messages":[HumanMessage(content=f"""
                I want to transform the data stored in the '/Users/yashgupta/Project/Data_Agent/data/extract/extracted_data.csv' file 
                and save the transformed data in the '/Users/yashgupta/Project/Data_Agent/data/transform' folder in the csv format.
                The transformation should filter the data to show bulbasaur pokemon only.""")]}
        )


