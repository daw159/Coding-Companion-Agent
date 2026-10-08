<div align="center">

# 💻 Coding Companion

### Your ideas. Your workspace. An AI companion that gets to work.

Create, edit, debug, and run code through a conversation — right from your terminal or browser.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Agent-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://docs.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Chat_UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tavily](https://img.shields.io/badge/Tavily-Web_Search-6366F1?style=for-the-badge)](https://tavily.com/)

**[Features](#-features) · [Quick start](#-quick-start) · [Usage](#-start-a-conversation) · [Tools](#-toolbox) · [Troubleshooting](#-troubleshooting)**

</div>

---

## ✨ Meet your coding companion

Coding Companion is a Python coding assistant built with LangChain’s `create_agent`. Describe what you want to build, and the agent selects tools to work with files, check syntax, execute programs, or search technical documentation.

It runs locally, supports **Gemini and Groq**, and keeps conversation history during your session. Choose the terminal for a simple chat workflow or the included Streamlit app for a browser interface.

> **Try this:** “Create `hello.py` that prints `Hello Dawood`, then run it.”

## 🚀 Features

| | Capability | What you can do |
| :---: | --- | --- |
| 💬 | **Conversational coding** | Build on earlier requests with session history. |
| 📁 | **Workspace management** | Create, read, move, rename, and explicitly delete files and folders. |
| ✏️ | **Precise editing** | Append text or replace one unique, exact block of existing code. |
| 🐛 | **Debugging workflow** | Read code, investigate a problem, edit it, and check the result. |
| ▶️ | **Local execution** | Run Python, C, C++, JavaScript, and PHP with optional standard input. |
| 🌐 | **Technical web search** | Look up documentation and unfamiliar errors through Tavily. |
| 🖥️ | **Two chat interfaces** | Use the terminal or the included Streamlit UI. |

## ⚡ Quick start

### 1. Clone the project

```bash
git clone https://github.com/daw159/Coding-Companion-Agent.git
cd Coding-Companion-Agent
```

You’ll need **Python 3.10+**, an internet connection, and an API key for your selected model provider. The project was originally used with Python 3.13 on Windows. Add a Tavily key to use web search.

### 2. Create a virtual environment

<details open>
<summary><strong>Windows · PowerShell</strong></summary>

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place of `python` in subsequent commands.

</details>

<details>
<summary><strong>macOS / Linux</strong></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
```

</details>

### 3. Install dependencies

Install the packages directly; this checkout does not include a `requirements.txt`.

```bash
python -m pip install langchain langchain-groq langchain-google-genai langchain-tavily python-dotenv
```

For the browser interface, also install:

```bash
python -m pip install streamlit
```

### 4. Create your coding workspace

Keep the agent application and its `.env` **outside** the working folder. A sibling directory makes that separation easy:

```text
projects/
├── Coding-Companion-Agent/     # Application and local configuration
└── Codingspace/                # Files the companion works on
