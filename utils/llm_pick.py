from langchain_mistralai import ChatMistralAI

def pick_llm(level:str)->str:
    """
    Function to pick the appropriate LLM based on the level of the query.
    
    Args:
        level (str): The level of the query, can be 'simple', 'intermediate', or 'complex'.
        
    Returns:
        str: The name of the LLM to be used for processing the query.
    """
    # if level.lower()== "low":
    #     llm = 