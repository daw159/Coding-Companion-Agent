import ast
import os
import shutil
import subprocess
import sys
import uuid

from pathlib import Path, PureWindowsPath
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv(Path(__file__).resolve().parent / ".env")

folder = os.getenv("WORK_DIR")

if not folder:
    raise ValueError("Set WORK_DIR in .env first.")

WORK_DIR = Path(folder).resolve(strict=True)

if not WORK_DIR.is_dir():
    raise ValueError("WORK_DIR must be a folder.")

if WORK_DIR == Path(WORK_DIR.anchor):
    raise ValueError("WORK_DIR cannot be an entire drive.")

APP_DIR = Path(__file__).resolve().parent

if APP_DIR.is_relative_to(WORK_DIR):
    raise ValueError("Keep the agent files and .env outside WORK_DIR.")


# ---------- Helper functions ----------

def safe_path(path: str, allow_root: bool = False) -> Path:
    """Check that a relative path stays inside WORK_DIR."""

    windows_path = PureWindowsPath(path)

    if (
        not path
        or Path(path).is_absolute()
        or windows_path.drive
        or windows_path.root
    ):
        raise ValueError("Use a relative path inside WORK_DIR.")

    parts = path.replace("\\", "/").split("/")

    if any(part == ".." or ":" in part for part in parts):
        raise ValueError("Access outside WORK_DIR is blocked.")

    target = WORK_DIR

    for part in parts:
        if part in ("", "."):
            continue

        if part.rstrip(" .") != part:
            raise ValueError("Names cannot end with a space or dot.")

        target = target / part

        if target.is_symlink():
            raise ValueError("Symbolic links are blocked.")

        if hasattr(target, "is_junction") and target.is_junction():
            raise ValueError("Folder junctions are blocked.")

        if target.exists():
            if not target.is_file() and not target.is_dir():
                raise ValueError("Special files are blocked.")

            if target.is_file() and target.stat().st_nlink > 1:
                raise ValueError("Hard-linked files are blocked.")

    target = target.resolve()

    if not target.is_relative_to(WORK_DIR):
        raise ValueError("Access outside WORK_DIR is blocked.")

    if target == WORK_DIR and not allow_root:
        raise ValueError("This operation cannot target WORK_DIR itself.")

    return target


def read_text(file: Path) -> str:
    if not file.is_file():
        raise ValueError("File does not exist.")

    with file.open("rb") as stream:
        content = stream.read(200_001)

    if len(content) > 200_000:
        raise ValueError("File exceeds the 200 KB limit.")

    if b"\x00" in content:
        raise ValueError("Only text/code files are supported.")

    return content.decode("utf-8")


def check_folder_tree(folder: Path):
    for parent, folders, files in os.walk(folder, followlinks=False):
        for name in folders + files:
            path = Path(parent) / name
            safe_path(str(path.relative_to(WORK_DIR)))


def run_command(command: list[str], stdin: str = "") -> str:
    """Run locally. This is not a filesystem sandbox."""

    try:
        result = subprocess.run(
            command,
            cwd=str(WORK_DIR),
            input=stdin,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            shell=False,
        )

        return (
            f"Exit code: {result.returncode}\n"
            f"Output:\n{result.stdout[:12000]}\n"
            f"Errors:\n{result.stderr[:12000]}"
        )

    except FileNotFoundError:
        return f"Error: {command[0]} was not found. Check installation and PATH."

    except subprocess.TimeoutExpired:
        return (
            "Error: The main process exceeded 15 seconds and was stopped. "
            "Any child processes may need to be stopped separately."
        )

    except Exception as error:
        return f"Error: {error}"


# ---------- Starter tools ----------

@tool
def list_files(path: str = ".") -> str:
    """List real files and folders inside WORK_DIR.
    Use relative paths. The default lists the working folder.
    """
    try:
        folder = safe_path(path, allow_root=True)

        if not folder.is_dir():
            return "Error: This is not a folder."

        lines = []

        for item in sorted(folder.iterdir()):
            try:
                checked = safe_path(str(item.relative_to(WORK_DIR)))
                kind = "folder" if checked.is_dir() else "file"
            except ValueError:
                kind = "blocked entry"

            lines.append(f"[{kind}] {item.name}")

            if len(lines) == 200:
                lines.append("Listing limited to 200 entries.")
                break

        return "\n".join(lines) or "Folder is empty."

    except Exception as error:
        return f"Error: {error}"


@tool
def read_file(path: str) -> str:
    """Read a UTF-8 text/code file inside WORK_DIR.
    Read existing files before editing or overwriting them.
    """
    try:
        return read_text(safe_path(path))
    except Exception as error:
        return f"Error: {error}"


@tool
def write_file(path: str, content: str) -> str:
    """Create or overwrite a text/code file inside WORK_DIR.
    Provide the complete new content. Missing parent folders are created.
    """
    try:
        file = safe_path(path)

        if len(content.encode("utf-8")) > 200_000:
            return "Error: Content exceeds 200 KB."

        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")

        return f"Wrote {len(content.splitlines())} lines to {path}."

    except Exception as error:
        return f"Error: {error}"


# ---------- Editing and conversion ----------

@tool
def edit_file(
    path: str,
    new_content: str,
    mode: str = "append",
    old_text: str = "",
) -> str:
    """Read an existing file, then append text or replace one exact block.
    append: add new_content at the end, including any necessary newlines.
    replace: old_text must match exactly once.
    """
    try:
        file = safe_path(path)
        content = read_text(file)

        if mode == "append":
            updated = content + new_content

        elif mode == "replace":
            if not old_text or content.count(old_text) != 1:
                return "Error: old_text must match exactly once. Read the file again."

            updated = content.replace(old_text, new_content, 1)

        else:
            return "Error: Mode must be append or replace."

        if len(updated.encode("utf-8")) > 200_000:
            return "Error: Updated content exceeds 200 KB."

        file.write_text(updated, encoding="utf-8")

        return f"Edited file: {path}"

    except Exception as error:
        return f"Error: {error}"


@tool
def file_conversion(source: str, destination: str) -> str:
    """Copy text or source code into a new .txt file.
    Preserve the original. Does not translate prose into code or languages.
    """
    try:
        source_file = safe_path(source)
        destination_file = safe_path(destination)

        if destination_file.suffix.lower() != ".txt":
            return "Error: Only text/code to .txt is supported."

        content = read_text(source_file)
        destination_file.parent.mkdir(parents=True, exist_ok=True)

        with destination_file.open("x", encoding="utf-8") as file:
            file.write(content)

        return f"Created {destination}. Original file preserved."

    except Exception as error:
        return f"Error: {error}"


# ---------- Files and folders ----------

@tool
def rename_file(source: str, destination: str) -> str:
    """Rename or move a file inside WORK_DIR without overwriting."""
    try:
        source_file = safe_path(source)
        destination_file = safe_path(destination)

        if not source_file.is_file():
            return "Error: Source file does not exist."

        if destination_file.exists():
            return "Error: Destination already exists."

        source_file.rename(destination_file)

        return f"Renamed {source} to {destination}."

    except Exception as error:
        return f"Error: {error}"


@tool
def create_folder(path: str) -> str:
    """Create a subfolder inside WORK_DIR, including missing parents."""
    try:
        safe_path(path).mkdir(parents=True, exist_ok=True)

        return f"Folder ready: {path}"

    except Exception as error:
        return f"Error: {error}"


@tool
def rename_folder(source: str, destination: str) -> str:
    """Rename or move a subfolder inside WORK_DIR without overwriting."""
    try:
        source_folder = safe_path(source)
        destination_folder = safe_path(destination)

        if not source_folder.is_dir():
            return "Error: Source folder does not exist."

        if destination_folder.exists():
            return "Error: Destination already exists."

        check_folder_tree(source_folder)
        source_folder.rename(destination_folder)

        return f"Renamed folder {source} to {destination}."

    except Exception as error:
        return f"Error: {error}"


@tool
def delete_file(path: str) -> str:
    """Delete a file only when the user explicitly requests its deletion."""
    try:
        file = safe_path(path)

        if not file.is_file():
            return "Error: File does not exist."

        file.unlink()

        return f"Deleted file: {path}"

    except Exception as error:
        return f"Error: {error}"


@tool
def delete_folder(path: str) -> str:
    """Delete a subfolder and all its contents.
    Use only when the user explicitly requests that folder's deletion.
    Never delete WORK_DIR itself.
    """
    try:
        folder = safe_path(path)

        if not folder.is_dir():
            return "Error: Folder does not exist."

        check_folder_tree(folder)
        shutil.rmtree(folder)

        return f"Deleted folder and its contents: {path}"

    except Exception as error:
        return f"Error: {error}"


# ---------- Execution and debugging ----------

@tool
def runs_file(path: str, stdin: str = "") -> str:
    """Run trusted Python, C, C++, JavaScript or PHP code locally.
    Read code first. Run only when requested or needed for a requested fix.
    Supply stdin for input() or cin. Local execution is not sandboxed.
    """
    try:
        file = safe_path(path)

        if not file.is_file():
            return "Error: File does not exist."

        extension = file.suffix.lower()

        if extension == ".py":
            command = [sys.executable, "-B", str(file)]

        elif extension == ".js":
            command = ["node", str(file)]

        elif extension == ".php":
            command = ["php", str(file)]

        elif extension in [".cpp", ".c"]:
            compiler = "g++" if extension == ".cpp" else "gcc"
            standard = "-std=c++17" if extension == ".cpp" else "-std=c11"

            if not shutil.which(compiler):
                return f"Error: {compiler} is not available in PATH."

            suffix = ".exe" if os.name == "nt" else ""
            executable = safe_path(
                f"build/program_{uuid.uuid4().hex}{suffix}"
            )
            executable.parent.mkdir(parents=True, exist_ok=True)

            compilation = subprocess.run(
                [
                    compiler,
                    standard,
                    str(file),
                    "-o",
                    str(executable),
                ],
                cwd=str(WORK_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                shell=False,
            )

            if compilation.returncode != 0:
                return (
                    "Compilation failed:\n"
                    f"{compilation.stdout[:6000]}\n"
                    f"{compilation.stderr[:6000]}"
                )

            return (
                f"Compiled file: {executable.relative_to(WORK_DIR)}\n"
                f"Compiler messages:\n{compilation.stderr[:3000]}\n"
                f"{run_command([str(executable)], stdin)}"
            )

        else:
            return "Error: Supported extensions: .py, .cpp, .c, .js, .php"

        return run_command(command, stdin)

    except subprocess.TimeoutExpired:
        return "Error: Compilation timed out."

    except Exception as error:
        return f"Error: {error}"


@tool
def debug_file(path: str) -> str:
    """Check source code for syntax errors without editing it.
    A passing syntax check does not prove the program's logic is correct.
    Use read_file and edit_file to diagnose and fix problems.
    """
    try:
        file = safe_path(path)

        if not file.is_file():
            return "Error: File does not exist."

        extension = file.suffix.lower()

        if extension == ".py":
            try:
                ast.parse(read_text(file), filename=str(file))
                return "Python syntax check passed. Logic was not checked."

            except SyntaxError as error:
                return (
                    f"Syntax error on line {error.lineno}: "
                    f"{error.msg}"
                )

        commands = {
            ".cpp": [
                "g++", "-std=c++17", "-Wall",
                "-Wextra", "-fsyntax-only", str(file)
            ],
            ".c": [
                "gcc", "-std=c11", "-Wall",
                "-Wextra", "-fsyntax-only", str(file)
            ],
            ".js": ["node", "--check", str(file)],
            ".php": ["php", "-l", str(file)],
        }

        command = commands.get(extension)

        if command is None:
            return "Error: Unsupported language for syntax checking."

        return run_command(command)

    except Exception as error:
        return f"Error: {error}"


# ---------- Web search ----------

@tool
def web_search(query: str) -> str:
    """Search coding documentation for an unfamiliar technical problem.
    Use technical terms or sanitized errors, never API keys or private code.
    """
    try:
        if not os.getenv("TAVILY_API_KEY"):
            return "Error: Set TAVILY_API_KEY in .env."

        from langchain_tavily import TavilySearch

        search = TavilySearch(max_results=3)
        result = search.invoke({"query": query})

        if not isinstance(result, dict):
            return str(result)[:6000]

        lines = []

        for item in result.get("results", []):
            lines.append(
                f"Title: {item.get('title', '')}\n"
                f"URL: {item.get('url', '')}\n"
                f"Content: {str(item.get('content', ''))[:1500]}"
            )

        return "\n\n".join(lines) or "No search results."

    except Exception as error:
        # Avoid exposing provider messages that might contain a key.
        return f"Search failed ({type(error).__name__}). Check your key and connection."


TOOLS = [
    list_files,
    read_file,
    write_file,
    edit_file,
    file_conversion,
    runs_file,
    rename_file,
    create_folder,
    rename_folder,
    delete_file,
    delete_folder,
    debug_file,
    web_search,
]