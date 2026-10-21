# from langchain_mistralai import ChatMistralAI
# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables from .env file

# def pick_llm(level:str)->str:
#     """
#     Function to pick the appropriate LLM based on the level of the query.
    
#     Args:
#         level (str): The level of the query, can be 'simple', 'intermediate', or 'complex'.
        
#     Returns:
#         str: The name of the LLM to be used for processing the query.
#     """
#     if level.lower()== "low":
#         llm = ChatMistralAI(model_name="ministral-3b-latest",temperature=0) #, model_kwargs={"reasoning_effort":"none"}'')
#     elif level.lower() == "medium":
#         llm = ChatMistralAI(model_name="ministral-8b-latest",temperature=0) #, model_kwargs={"reasoning_effort":"none"})
#     elif level.lower() == "high":
#         llm = ChatMistralAI(model_name="mistral-large-latest",temperature=0) #, model_kwargs={"reasoning_effort":"none"})
#     else:
#         raise ValueError(f"Unsupported level: {level}. ")

#     return llm

# llm_obj=pick_llm("low")
# print(llm_obj.invoke("What is the capital of France?"))


import os
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def pick_llm(level: str) -> BaseChatModel:
    level = level.lower()
    
    # Translate 0.0.0.0 binding address to localhost for client requests
    local_host = os.getenv("API_HOST", "localhost")
    if local_host == "0.0.0.0":
        local_host = "localhost"
        
    local_port = os.getenv("API_PORT", "8080")
    base_url = f"http://{local_host}:{local_port}"
    
    if level == "low":
        # Ultra-fast lightweight model for simple tasks / code completion
        target_model = os.getenv("MODEL_LOW", "qwen2.5-coder:1.5b-base")
        return ChatOllama(model=target_model, temperature=0, base_url=base_url)
    
    elif level == "medium":
        # Balanced middle-tier model
        target_model = os.getenv("MODEL_MEDIUM", "gemma4:e2b")
        return ChatOllama(model=target_model, temperature=0, base_url=base_url)
    
    elif level == "high":
        # High-capacity model for complex reasoning tasks
        target_model = os.getenv("MODEL_HIGH", "gemma4:latest")
        return ChatOllama(model=target_model, temperature=0, base_url=base_url)
        
    else:
        raise ValueError(f"Unsupported level: '{level}'. Please use 'low', 'medium', or 'high'.")

# --- Example Usage ---
if __name__ == "__main__":
    for tier in ["low", "medium", "high"]:
        llm = pick_llm(tier)
        print(f"Level [{tier.upper()}] initialized with model: {llm.model}")