import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#all this was needed to access a sibling directory from a different directory in python.

from utils.llm_pick import pick_llm #using a function in python
from models.schema import AgentSchema
from langchain_core.messages import HumanMessage
from utils.database import DatabaseUtil

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
    state.messages = state.messages+[HumanMessage(content=f"Response")]
    return state # puri state ko return kar rahe hai

def prompt_query_context(state: AgentSchema) -> AgentSchema:

    curated_question = state.curated_ques

    """Context wali query banane ke liye lagega - data context : kiske context (column name, db name, table name etc.) se query tayyar hogi
    
    For which we need data.
    
    we will create a database in the utility.""" 

    conn_details = {
        "host": os.environ['host'],
        "port": os.environ['port'],
        "user": os.environ['user'],
        "password": os.environ['password'],
        "dbname": os.environ['database']
    }



    obj = DatabaseUtil(conn_details) # isme databse ki detail jaise table names and their structure ayega aur usko schema_info me save kara lenge

    schema_info = obj.schema_details("public") #public db ko access karne ke liye, else wo information_schema bhi access kar sakta hai

    # Constructing the prompt query for the agent to generate the SQL query - it is guardrailed and a note is given to limit the no. of output to 10 rows unless specifically asked and strict sql fromat is requested without any extra word.
    # ek raw prompt w/o any table row details  - this will turn that into well structured query

    #compiling all into one var 'prompt'
    prompt = f""" 
    You are an SQL analyst agent. Your task is to convert the user's natural language 
    query into Postgres SQL query that can be executed on the database. You are provided 
    with the user's original query and the schema details of the database, including
    table names, column names, data types, and sample data for each table so that 
    you can understand the structure of the database and generate an accurate SQL query.
    Unless user explicitly asks for specific number of rows, always limit the output to 10 rows.
    Note - Just generate the SQL query without any explanation or additional text because
    this query will be executed directly on the database. So, the output should be SQL
    ready to be executed without any modifications.  
    
    User's Original Query: {curated_question}

    Database Schema Details:
    {schema_info}
    
    """    
    state.prompt_query_context = prompt

    llm = pick_llm("medium")
    generated_sql_query = llm.invoke(prompt) # get the final answer from the llm

    state.generated_sql_query = generated_sql_query # state i.e. schema.py>AgentSchema me save kara diya

    return state # state i.e. schema.py>AgentSchema ko hi return kiya jayega 

    # ==> ChatMistralAI(model_name="ministral-8b-latest",temperature=0).invoke(human_query -> polished query -> database schema + polished query -> "FINAL QUERY") ==> saved in schema.py>>AgentSchema

    

