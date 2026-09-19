<!--
# 🤖 Agentic AI - Data Agent

An intelligent, multi-agent system built with **LangGraph** that processes natural language queries by routing them to specialized agents for **SQL database analytics** or **ETL workflows**.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🏗️ System Architecture

```
                   ┌─────────────────────────┐
                   │   Data Agent (Router)   │
                   └────────────┬────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
    ┌──────────────────┐                ┌──────────────────┐
    │  SQL Analyst     │                │   ETL Analyst    │
    └─────────┬────────┘                └─────────┬────────┘
              │                                   │
              ├─► Context & Schema Gathering      ├─► API Data Extraction
              ├─► SQL Generation & Safety Check   ├─► Pandas Transformations
              └─► Query Execution & Answers       └─► Code Execution & Output
```

---

## ✨ Core Features

* **Intelligent Intent Routing:** Automatically classifies natural language user input into SQL or ETL tasks.
* **SQL Analyst Agent:** Converts natural language to safe PostgreSQL queries, performs strict schema validation, and blocks destructive operations (`DROP`, `DELETE`, `UPDATE`).
* **ETL Analyst Agent:** Automatically extracts data from external APIs and transforms local datasets (CSV, JSON, Parquet) using Pandas.
* **Dynamic Model Tiering:** Routes queries across fast/cost-effective LLMs or premium models (e.g., Claude 3 Opus) based on task complexity.

---

## 🚀 Quickstart

### 1. Prerequisites & Setup

* **Python:** 3.12+
* **Database:** PostgreSQL instance running locally or remotely.

```bash
# Clone repository and navigate inside
cd Data_Agent

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
* **Create a .env file in the root directory:**


  ```bash
    # API Keys
  ANTHROPIC_API_KEY=your_claude_api_key
  OPENAI_API_KEY=your_openai_api_key
  
  # Database Connection
  host=localhost
  port=5432
  user=postgres
  password=your_password
  database=data_agent_db
  
  # Model Selection
  LLM_MODEL_LOW=gpt-3.5-turbo
  LLM_MODEL_MEDIUM=gpt-4-turbo
  LLM_MODEL_HIGH=claude-3-opus
  ```
## 💻 Usage
**Run Main Agent**
```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

# Example 1: Database Query (SQL Agent)
sql_response = data_agent.invoke({
    "messages": [HumanMessage(content="Show me the top 5 users with the highest ratings")],
    "route_response": ""
})

# Example 2: API Extraction & Transformation (ETL Agent)
etl_response = data_agent.invoke({
    "messages": [HumanMessage(content="Extract data from '[https://pokeapi.co/api/v2/pokemon](https://pokeapi.co/api/v2/pokemon)' and save as CSV to data/extract")],
    "route_response": ""
})
```
**Run via Command Line**
```bash
# Execute full workflow
python main.py

# Run individual sub-agents directly
python agents/sql_analyst.py
python agents/etl_analyst.py
```

## 📁 Repository Structure
```bash
Data_Agent/
├── agents/             # Sub-agent implementations (router, sql, etl)
├── Models/             # Pydantic schemas and state management
├── utils/              # PostgreSQL drivers, ETL tools, & dynamic LLM selectors
├── data/               # Input/output workspace (extract/ and transform/)
├── feed_db.py          # Database initialization script
└── main.py             # Main entry point
```

## 🛡️ Security Features
SQL Guardrails: Queries undergo strict safety parsing prior to database execution to prevent data mutation or deletion.

Sandboxed Code Execution: Standardized input validation and restricted environment limits for runtime Pandas operations.
-->

# 🤖 Agentic AI - Data Agent

An intelligent, multi-agent system built with **LangGraph** that processes natural language queries by routing them to specialized agents for **SQL database analytics** .

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🏗️ System Architecture

```
                   ┌─────────────────────────┐
                   │   Data Agent (Router)   │
                   └────────────┬────────────┘
                                │
                                ▼
                      ┌──────────────────┐                
                      │  SQL Analyst     │
                      └─────────┬────────┘                
                                │
                                ├─► Context & Schema Gathering      
                                ├─► SQL Generation & Safety Check   
                                └─► Query Execution & Answers       
```

---

## ✨ Core Features

* **Intelligent Intent Routing:** Automatically classifies natural language user input into SQL.
* **SQL Analyst Agent:** Converts natural language to safe PostgreSQL queries, performs strict schema validation, and blocks destructive operations (`DROP`, `DELETE`, `UPDATE`).
* **Dynamic Model Tiering:** Routes queries across fast/cost-effective LLMs or premium models (e.g., Claude 3 Opus) based on task complexity.

---

## 🚀 Quickstart

### 1. Prerequisites & Setup

* **Python:** 3.12+
* **Database:** PostgreSQL instance running locally or remotely.

```bash
# Clone repository and navigate inside
cd Data_Agent

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
* **Create a .env file in the root directory:**


  ```bash
    # API Keys
  ANTHROPIC_API_KEY=your_claude_api_key
  OPENAI_API_KEY=your_openai_api_key
  
  # Database Connection
  host=localhost
  port=5432
  user=postgres
  password=your_password
  database=data_agent_db
  
  # Model Selection
  LLM_MODEL_LOW=gpt-3.5-turbo
  LLM_MODEL_MEDIUM=gpt-4-turbo
  LLM_MODEL_HIGH=claude-3-opus
  ```
## 💻 Usage
**Run Main Agent**
```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

# Example 1: Database Query (SQL Agent)
sql_response = data_agent.invoke({
    "messages": [HumanMessage(content="Show me the top 5 users with the highest ratings")],
    "route_response": ""
})
```
**Run via Command Line**
```bash
# Execute full workflow
python main.py

# Run individual sub-agents directly
python agents/sql_analyst.py
```

## 📁 Repository Structure
```bash
Data_Agent/
├── agents/             # Sub-agent implementations (router, sql)
├── Models/             # Pydantic schemas and state management
├── utils/              # PostgreSQL drivers, & dynamic LLM selectors
├── data/               # Input/output workspace (extract/ and transform/)
├── feed_db.py          # Database initialization script
└── main.py             # Main entry point
```

## 🛡️ Security Features
SQL Guardrails: Queries undergo strict safety parsing prior to database execution to prevent data mutation or deletion.

Sandboxed Code Execution: Standardized input validation and restricted environment limits for runtime Pandas operations.

