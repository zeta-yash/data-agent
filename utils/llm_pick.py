from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

def pick_llm(level:str)->str:
    """
    Function to pick the appropriate LLM based on the level of the query.
    
    Args:
        level (str): The level of the query, can be 'simple', 'intermediate', or 'complex'.
        
    Returns:
        str: The name of the LLM to be used for processing the query.
    """
    if level.lower()== "low":
        llm = ChatMistralAI(model_name="ministral-3b-latest",temperature=0)
    elif level.lower() == "medium":
        llm = ChatMistralAI(model_name="ministral-8b-latest",temperature=0)
    elif level.lower() == "high":
        llm = ChatMistralAI(model_name="mistral-large-latest",temperature=0)
    else:
        raise ValueError(f"Unsupported level: {level}. ")

    return llm

# llm_obj=pick_llm("low")
# print(llm_obj.invoke("What is the capital of France?"))