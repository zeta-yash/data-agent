import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#all this was needed to access a sibling directory from a different directory in python.

from utils.llm_pick import pick_llm #using a function in python
from models.schema import AgentSchema

# ===============AI Agent Code===========================

def curate_ques(state: AgentSchema) -> AgentSchema:
    """
    Curates the user question based on the messages in the state
    Args:
     state(AgentSchema) : The current state of the agent.
      
    Returns:
     the updated state with the curated question.
      
    AgentSchema is the basket of all the context (history) of messages along, in each cycle """

    """
    #AgentSchema ko as a property use kar rahe hai, jisme messages, user_question, curated_ques, prompt_query_context, is_safe, generated_sql_query, sql_query_execution_result, final_answer ye sab properties hai.

    #usse pehle user question ko state se le rahe hai, jisse hum curated question me use karenge.

    # state.user_question is an pydantic model object of AgentSchema class, is liye state.user_question ko access karne ke liye dot notation use kar rahe hai."""

    user_question = state.user_question 
    llm = pick_llm("low")  # Pick the appropriate LLM based on the level of the query
    response = llm.invoke(f"Curate the following question: {user_question}")

    state.curated_ques = response  # Update the state with the curated question
    return state # puri state ko return kar rahe hai

def prompt_query_context(state: AgentSchema) -> AgentSchema:

    curated_ques = state.curated_ques

    """Context wali query banane ke liye lagega - data context : kiske context (column name, db name, table name etc.) se query tayyar hogi
    
    For which we need data.
    
    we will create a database in the utility."""



