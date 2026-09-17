import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#all this was needed to access a sibling directory from a different directory in python.

from utils.llm_pick import pick_llm #using a function in python
from models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import HumanMessage, AIMessage
from utils.database import DatabaseUtil
from langgraph.graph import StateGraph, START,END 
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
    response = llm.invoke(f"Curate the following question: {user_question}").content

    state.curated_ques = response  # Update the state with the curated question
    state.messages = state.messages+[HumanMessage(content=f"{response}")]
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



    obj = DatabaseUtil(conn_details) # isme databse ki detail jaise table names and their structure ayega aur usko schema_info me save kara lenge - constructor

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

    return state 
    # state i.e. schema.py>AgentSchema ko hi return kiya jayega 
 
    # ==> ChatMistralAI(model_name="ministral-8b-latest",temperature=0).invoke(human_query -> polished query using low llm -> (database schema + polished query) using medium llm -> "FINAL QUERY") ==> saved in schema.py>>AgentSchema

#Generate SQL Query node============''THE MAIN QUERY WE wanted to create''============================
def generate_sql(state: AgentSchema) -> AgentSchema:

    prompt = state.prompt_query_context

    llm = pick_llm("medium")
    generated_sql_query = llm.invoke(prompt).content # get the final answer from the llm = THE MAIN QUERY WE wanted to create.

    state.generated_sql_query = generated_sql_query # state i.e. schema.py>AgentSchema me save kara diya
    return state


def is_safe_sql(state: AgentSchema) -> AgentSchema:

    sql_query = state.generated_sql_query

    llm = pick_llm('medium')
    llm_judge = llm.with_structured_output(JudgeSchema)

    prompt = f"""
    You are an SQL Judge for data security. Your task is to determine whether the SQL query is safe or not. The SQL query should only be used for data retrieval and should not modify the database in any way. Neither the SQL query nor the prompt should contain any SQL commands that can modify the database, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or any other commands that can change the structure or content of the database. If the SQL query is safe, respond with 'Yes' otherwise respond with 'No'. Additionally, provide comments explaining your decision.
    
    Here's the SQL query to evaluate: {sql_query}"""
    
    response = llm_judge.invoke(prompt). model_dump () # Get the structured output as a dictionary

    state.is_safe = response['answer']
    state.comments = response['comments']

    return state

#Canceled SQL query node
def canceled_sql(state: AgentSchema) -> AgentSchema:
    comments=state.comments

    state.final_answer = f"The generated SQL query was deemed unsafe to execute. The reason provided by the judge is: {comments}. Therefore, the SQL query will not be executed."
    state.messages = state.messages + [AIMessage(content=f"{state.final_answer}")]  # Append the final answer to the messages list  

#========= function to run the main query generated by SQL============

def execute_sql(state: AgentSchema) -> AgentSchema:

    sql_query = state.generated_sql_query

    conn_details = {
    "host": "localhost",
    "port": 5432,
    "user": "yashgupta",
    "password": "root",
    "dbname": "postgres"
}
    obj = DatabaseUtil(conn_details)

    execution_result = obj.execute_sql(sql_query)
    state.sql_query_execution_result = execution_result
    return state

def represent_final_answer(state: AgentSchema) -> AgentSchema: 
    # this will be the final answer to the user's question in his local language (executed query to query result in human form) and also added in AI response list.

    execution_result = state.sql_query_execution_result
    curated_question = state.curated_ques

    llm = pick_llm("low")

    prompt = f"""
    You are an SQL analyst agent. Your task is to provide a final answer to the user based on the
    execution result of the SQL query and the user's original question. The final answer should be
    concise, clear, and directly address the user's query. Avoid including any SQL code or technical
    details in the final answer. The final answer should be in a user-friendly format that is easy to
    understand. If the execution result is empty or does not provide a clear answer to the user's question, explain this in the final answer. \n
    Here is the execution result: {execution_result} \n
    Here is the user's original question: {curated_question}
    """

    llm_response = llm.invoke(prompt).content  # Get the final answer from the LLM
    # .content is used to get only the content of the response, not the metadata like tokens and other metadata.
    state.final_answer = llm_response
    state.messages = state.messages + [AIMessage(content=f"{llm_response}")]  # Append the final answer to the messages list

    return state

# ---------------------------------Graph Building------------------------------------

sql_agent_graph = StateGraph(AgentSchema)


# Nodes (Pehle string name, fir function)
sql_agent_graph.add_node("curate_ques", curate_ques)
sql_agent_graph.add_node("prompt_query_context", prompt_query_context)
sql_agent_graph.add_node("generate_sql", generate_sql) 
sql_agent_graph.add_node("is_safe_sql", is_safe_sql)
sql_agent_graph.add_node("canceled_sql", canceled_sql)
sql_agent_graph.add_node("execute_sql", execute_sql)
sql_agent_graph.add_node("represent_final_answer", represent_final_answer)

# Edges
sql_agent_graph.add_edge(START, "curate_ques")
sql_agent_graph.add_edge("curate_ques", "prompt_query_context")
sql_agent_graph.add_edge("prompt_query_context", "generate_sql")
sql_agent_graph.add_edge("generate_sql", "is_safe_sql")

# Conditional Edge Function
def is_safe_sql_edge(state: AgentSchema) -> str:
    is_safe = state.is_safe

    if is_safe.lower == "yes":
        return "execute_sql"
    else:
        return "canceled_sql"


# these edges will act as dotted edges in the graph representing conditional edges 
sql_agent_graph.add_conditional_edges("is_safe_sql",is_safe_sql_edge,
                                      {"execute_sql":"execute_sql",
                                       "canceled_sql":"canceled_sql"})


sql_agent_graph.add_edge("canceled_sql", END)
sql_agent_graph.add_edge("execute_sql", "represent_final_answer")
sql_agent_graph.add_edge("represent_final_answer",END)

# compile the graph

sql_analyst = sql_agent_graph.compile()

# display the graph
# from IPython.display import display, Image
# img = Image(sql_analyst.get_graph().draw_mermaid_png())
# with open ("sql_analyst.png", "wb") as f:
#     f.write(img.data)


input_schema = {
        "messages": [],
        "user_question": "What are the different types of Payment Methods we have in our database",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }

sql_analyst_response = sql_analyst.invoke(input_schema)


print(sql_analyst_response['curated_ques'])
print("****************************************************")
print(sql_analyst_response['generated_sql_query'])
print("****************************************************")
print(sql_analyst_response['messages'])
print("****************************************************")
print(sql_analyst_response['sql_query_execution_result'])
print("****************************************************")
print(sql_analyst_response['prompt_query_context'])


