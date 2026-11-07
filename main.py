from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    query = "I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in csv format."
    print(f"Starting Data Agent with query: {query}\n")

    response = data_agent.invoke(
        {"messages": [HumanMessage(content=query)], "route_response": ""}
    )
    print("\n--- Final Agent Response ---")
    print(response['messages'][-1].content)