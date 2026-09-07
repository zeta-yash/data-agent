import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#all this was needed to access a sibling directory from a different directory in python.

from utils.llm_pick import pick_llm #using a function in python
from models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import HumanMessage
from utils.database import DatabaseUtil

llm = pick_llm("medium")

llm_judge = llm.with_structured_output(JudgeSchema)
