# 🤖 Agentic AI - Data Agent

An intelligent, multi-agent system built with **LangGraph** that processes natural language queries by routing them to specialized agents for **SQL database analytics** or **ETL workflows** using locally-hosted LLMs via **Ollama**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Local%20LLM-Ollama-black.svg)](https://ollama.com/)
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
              ├─► SQL Generation & Safety Judge   ├─► Pandas Transformations
              └─► Query Execution & Answers       └─► Code Execution & Output
```

---

## ✨ Core Features

* **Intelligent Intent Routing:** Automatically analyzes user intent and routes queries to either the SQL or ETL pipeline.
* **SQL Analyst Agent:** Converts natural language to Postgres queries, inspects live database schema context, validates query safety with an AI safety judge (blocking destructive operations like `DROP`, `DELETE`, `UPDATE`), and returns friendly answers.
* **ETL Analyst Agent:** Extracts data from REST APIs into CSV/JSON/Parquet, loads sample data context, generates Pandas transformation code dynamically, and executes the transformation locally.
* **Local AI Model Tiering:** Routes requests across distinct local model tiers (`low`, `medium`, `high`) powered by a local Ollama instance for zero-cost, private, offline execution.

---

## ⚙️ Prerequisites

Before getting started, make sure you have the following installed on your machine:

1. **Python 3.11+**
2. **[uv](https://github.com/astral-sh/uv)** (recommended fast Python package manager) or standard `pip`
3. **[Ollama](https://ollama.com/)** (to run local LLMs)
4. **PostgreSQL** instance running locally or remotely

---

## 📥 Cloning & Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Data_Agent.git
cd Data_Agent
```

### 2. Setup Virtual Environment & Dependencies

#### Option A: Using `uv` (Recommended)
```bash
# Automatically creates virtual environment (.venv) and syncs dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate       # macOS / Linux
# or: .\.venv\Scripts\activate  # Windows
```

#### Option B: Using standard `venv` & `pip`
```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# or: .\.venv\Scripts\activate  # Windows

pip install -e .
```

---

## 🧠 Establishing Local AI Model APIs (Ollama)

This project runs **100% locally** using Ollama for model serving. Follow these steps to establish the AI model APIs:

### 1. Install & Launch Ollama

* **macOS:**
  ```bash
  brew install ollama
  ollama serve
  ```
  *(Or download the macOS App directly from [ollama.com](https://ollama.com/download))*
* **Linux:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
* **Windows:** Download the installer from [ollama.com](https://ollama.com/download/windows).

Make sure Ollama is running in the background. By default, it serves its API on `http://127.0.0.1:11434`.

### 2. Pull the Required Models

The agent uses three tiers defined in `utils/llm_pick.py`:

| Tier | Purpose | Recommended Model | Pull Command |
| :--- | :--- | :--- | :--- |
| **Low** | Quick routing, query curation, formatting | `qwen2.5-coder:1.5b` | `ollama pull qwen2.5-coder:1.5b` |
| **Medium** | SQL generation, safety judge, Pandas code | `qwen2.5-coder:7b` | `ollama pull qwen2.5-coder:7b` |
| **High** | Complex multi-step reasoning | `qwen2.5-coder:14b` or `llama3.1:8b` | `ollama pull qwen2.5-coder:14b` |

> [!IMPORTANT]
> **Use Chat/Instruct models, not `-base` models:**
> Always use instruct-tuned models (e.g. `qwen2.5-coder:1.5b`), never foundational `-base` models (e.g. `qwen2.5-coder:1.5b-base`). Base models do not know chat end-of-turn tokens and will ramble endlessly, causing terminal requests to hang.

### 3. Verify the Ollama API

Verify that your local Ollama API is active and models are available:

```bash
curl http://127.0.0.1:11434/api/tags
```

---

## 🗄️ Database Setup (PostgreSQL)

Ensure PostgreSQL is running locally and that you have a database created:

```bash
# Start PostgreSQL (macOS Homebrew example)
brew services start postgresql@16

# Create database if not already existing
createdb postgres
```

---

## 🔑 Environment Configuration (`.env`)

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to match your local setup:

```env
# Ollama Local Model Configuration
MODEL_LOW=qwen2.5-coder:1.5b
MODEL_MEDIUM=qwen2.5-coder:7b
MODEL_HIGH=qwen2.5-coder:14b
API_HOST=127.0.0.1
API_PORT=11434

# PostgreSQL Database Connection
host=localhost
port=5432
user=yashgupta
password=root
database=postgres
```

---

## 💻 Usage & Execution

### 1. Run the Full Multi-Agent System

Execute the main entry point:

```bash
python -u main.py
```

The system will:
1. Receive your natural language query.
2. Route it via the **Data Agent Router** to the appropriate sub-agent (`SQL Analyst` or `ETL Analyst`).
3. Display real-time console feedback as tools and LLMs execute.
4. Print the final curated response.

### 2. Run Individual Sub-Agents Directly

You can also run sub-agents independently for testing:

```bash
# Test the SQL Analyst agent
python agents/sql_analyst.py

# Test the ETL Analyst agent
python agents/etl_analyst.py
```

---

## 📁 Repository Structure

```
Data_Agent/
├── agents/             # LangGraph agent definitions
│   ├── data_agent.py   # Master router agent orchestrating sub-agents
│   ├── sql_analyst.py  # SQL generation, security judge, and DB executor
│   └── etl_analyst.py  # Tool-calling agent for extraction and Pandas ETL
├── models/             # Pydantic schemas and LangGraph state definitions
│   └── schema.py       # AgentSchema, JudgeSchema, ETLAgentSchema, etc.
├── utils/              # Shared helper modules
│   ├── database.py     # PostgreSQL connection & schema discovery driver
│   ├── etl_tools.py    # API fetcher and isolated Pandas code executor
│   └── llm_pick.py     # Multi-tier local Ollama model loader
├── data/               # Local workspace for ETL runs
│   ├── extract/        # Target folder for extracted API datasets
│   └── transform/      # Target folder for transformed datasets
├── main.py             # Top-level entry point script
├── pyproject.toml      # Project metadata & dependencies (uv / pip)
├── .env.example        # Environment variable template
└── README.md           # Documentation
```

---

## 🛡️ Security & Guardrails

* **SQL Judge Guardrail:** Every generated SQL query is inspected by an independent LLM judge before execution. Queries containing data manipulation commands (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`) are blocked immediately.
* **Safe Code Execution Context:** The ETL analyst executes Pandas code within an isolated global scope with required modules pre-loaded (`pd`, `os`), raising errors if unexpected operations occur.
