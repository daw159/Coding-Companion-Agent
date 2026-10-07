Coding Companion
A Python coding assistant built with LangChain's create_agent. Chat with it to create, read, edit, debug, and run code in a configured working folder.
The companion uses an LLM to choose tools, Python functions to perform actions, and Tavily for technical web searches. It runs locally without Docker.
Features
- Multi-turn terminal chat with conversation history during the session.
- File and folder management inside a configured workspace.
- Exact text replacement and appending to existing files.
- Syntax checks and local execution for supported languages.
- Web search for unresolved technical questions.
- Optional Streamlit chat interface.
Project files
File	Purpose
agent.py	System prompt, agent setup, and terminal chat loop
tools.py	Tools and workspace path checks
llm.py	Model selection and API key loading
.env	Local API keys and working folder; never commit
.env.example	Configuration template with placeholder keys
requirements.txt	Python dependencies
.gitignore	Files and folders excluded from Git
app.py	Optional Streamlit GUI, if added
README.md	Setup and usage instructions


Keep the working folder separate from the application files and .env. The examples below use a sibling folder named Codingspace.
Requirements
- Python 3.10 or newer. The project was used with Python 3.13 on Windows.
- Internet access for model requests and web searches.
- A Groq or Gemini API key, depending on the model selected in llm.py.
- A Tavily API key for the web search tool.
- Optional language runtimes listed below.
Installation
Open PowerShell in the project folder:
cd "G:\Codes\5 sem codes\AI\agentcompetition"
If downloading from GitHub, clone your repository first and open its folder.
1. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
If PowerShell blocks activation, use the environment's Python directly instead:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe agent.py
2. Install dependencies
Put these packages in requirements.txt:
langchain
langchain-groq
langchain-google-genai
langchain-tavily
python-dotenv
Then install them:
python -m pip install -r requirements.txt
Alternatively:
python -m pip install langchain langchain-groq langchain-google-genai langchain-tavily python-dotenv
Streamlit is optional:
python -m pip install streamlit
3. Create the working folder
New-Item -ItemType Directory -Force "G:\Codes\5 sem codes\AI\Codingspace"
The folder must exist before starting the companion. Change this path to match your computer.
4. Configure environment variables
Create .env.example with placeholders:
GROQ_API_KEY=your_groq_api_key_here
GEMINI_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
WORK_DIR=G:/Codes/5 sem codes/AI/Codingspace
Copy it to .env:
Copy-Item .env.example .env
Replace the placeholders in .env with your own keys. Only the selected model's key is required for chat. Tavily is required when using web search.
API key dashboards:
- Groq: Groq Console
- Gemini: Google AI Studio
- Tavily: Tavily
llm.py loads the model key. tools.py loads WORK_DIR and the Tavily key. Keep actual keys out of your README, Git commits, and screenshots. Replace any key that has already been shared publicly.
5. Choose the model
In llm.py, select the provider:
GEMINI = "google_genai:gemini-3.1-flash-lite"
GROQ = "groq:openai/gpt-oss-120b"

MODEL = GROQ

if MODEL == GEMINI:
    api_key = os.getenv("GEMINI_KEY")
else:
    api_key = os.getenv("GROQ_API_KEY")
These are the model identifiers used in the project. Availability depends on your provider account. The key must match the selected provider.
Run the terminal companion
From the project folder:
python agent.py
Example conversation:
Coding Companion
Working folder: G:\Codes\5 sem codes\AI\Codingspace
Type exit to stop.

You: Create hello.py that prints "Hello Dawood", then run it.
Agent: ...

You: Read hello.py and change the greeting to "Welcome Dawood".
Agent: ...

You: exit
Use relative paths such as hello.py or practice/main.cpp in your requests.
Type exit or quit to close the terminal session. You can also press Ctrl+C. Conversation history lasts for the current process; created files remain after it closes.
Available tools
Tool	What it does
list_files	Lists files and folders
read_file	Reads a UTF-8 text file
write_file	Creates a file or overwrites its complete contents
edit_file	Appends text or replaces one unique exact block
file_conversion	Copies text or source code into a new .txt file
rename_file	Renames or moves a file within the workspace
create_folder	Creates a folder, including missing parent folders
rename_folder	Renames or moves a subfolder within the workspace
delete_file	Deletes a file when explicitly requested
delete_folder	Deletes a subfolder and its contents when explicitly requested
runs_file	Runs supported source files and returns program output
debug_file	Checks syntax and reports available compiler warnings
web_search	Searches for technical information with Tavily


file_conversion does not translate programming languages. Copying Python code to .txt preserves its text; changing an extension does not convert prose into C++.
debug_file checks syntax. The agent can then read, edit, and test code to investigate a bug, but a successful syntax check alone does not establish logical correctness.
Supported execution languages
Language	Extension	Required program
Python	.py	The Python interpreter running the companion
C	.c	gcc on PATH
C++	.cpp	g++ on PATH
JavaScript	.js	node on PATH
PHP	.php	php on PATH


Python packages do not install these additional compilers or runtimes. Install them separately if needed, then reopen your terminal and check:
gcc --version
g++ --version
node --version
php --version
C and C++ compilation creates executables in the workspace's build folder. If a program needs input, include that input in your request.
Optional GUI
If you have added the Streamlit app.py, install Streamlit and run:
python -m pip install streamlit
python -m streamlit run app.py
Open the local address displayed in the terminal. The GUI uses the same agent, tools, and WORK_DIR. Its Clear chat button clears conversation history without deleting project files.
Keep the terminal chat loop inside if __name__ == "__main__": in agent.py so importing the agent from app.py does not start terminal input.
Example requests
- "List the files in my workspace."
- "Create practice/main.py with a function that checks whether a number is prime."
- "Read practice/main.py and add examples for 1, 2, and 9."
- "Run practice/main.py and show the output."
- "Check main.cpp for syntax errors and fix them."
- "Copy hello.py into hello.txt."
- "Rename hello.py to greeting.py."
- "Search the official Python documentation for pathlib usage."
- "Delete the folder old_practice and everything inside it."
How it works
create_agent receives the model, tools, and system prompt. The model chooses a tool when needed. LangChain executes the tool and sends its result back to the model. This repeats until the model returns an answer.
After each successful turn, agent.py keeps the returned messages and passes them into the next request. This provides conversation history within the session. The project does not need a manually built StateGraph for this standard model-and-tools loop.
Workspace and execution limits
File tools validate paths against WORK_DIR and reject paths outside it, including traversal and unsupported links. The application files and credentials should remain outside the working folder.
Local execution is not a security sandbox. Without Docker or another operating-system sandbox, executed code runs with your user permissions and can access files or the network beyond WORK_DIR. The system prompt asks the agent to respect the workspace, but it cannot enforce operating-system isolation. Run code you trust.
Deletion should happen only on an explicit user request. Review the target carefully because deleted files and overwritten contents may not be recoverable. If a request fails after a tool runs, file changes may already have happened; inspect the workspace before retrying.
Git ignore rules
Use this .gitignore:
# Local credentials
.env
.env.*
!.env.example

# Python cache and environments
__pycache__/
*.py[cod]
.venv/
venv/

# Agent workspace, if inside the repository
Codingspace/

# Compiler outputs
build/
*.exe
*.o
Commit your source files, README.md, requirements.txt, and .env.example containing placeholders. A sibling Codingspace folder is already outside the repository; the ignore rule applies if you later put that folder inside it.
If .env is already tracked, stop tracking it with:
git rm --cached .env
This keeps the local file but does not remove secrets from old commits. Replace exposed keys.
Troubleshooting
Problem	What to check
FileNotFoundError during startup	Create the folder in WORK_DIR and check its spelling
Created files are missing from VS Code	Open Codingspace, or use File > Add Folder to Workspace
ModuleNotFoundError	Install dependencies with the same Python interpreter used to run the agent
Authentication error	Check the selected model, matching API key, and .env location
Rate limit or quota error	Check provider quota and retry after the provider's indicated delay
Compiler/runtime not found	Install the relevant program and add it to PATH
Path rejected	Use a relative path inside WORK_DIR
Web search fails	Check TAVILY_API_KEY, connectivity, and Tavily quota
Tool loop reaches its limit	Simplify the request and inspect completed changes before retrying
GUI starts terminal input	Put the terminal loop under the main guard in agent.py


Quick test
After setup, ask:
Create hello.py that prints "Hello Dawood", then run it.
Check that hello.py exists in Codingspace and that the reported program output contains Hello Dawood.
