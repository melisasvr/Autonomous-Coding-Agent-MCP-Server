"""
Groq Autonomous Coding Agent - CLI Runner
Usage:
    python run_agent.py "Build a calculator" --dir ./myproject
    python run_agent.py --chat
    python run_agent.py "Create a script" --plan-only
"""

import asyncio
import argparse
import os
import sys
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from agent.groq_client import GroqAgent
from tools.file_tools import FileTools
from tools.shell_tools import ShellTools

# ── Colours ────────────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    DIM     = "\033[2m"

def c(color, text):
    return f"{color}{text}{C.RESET}"

def print_header(args_dir, iterations, model, mode="autonomous"):
    print()
    print(c(C.CYAN, C.BOLD + "╔══════════════════════════════════════════════╗"))
    print(c(C.CYAN,         "║   🤖  Groq Autonomous Coding Agent           ║"))
    print(c(C.CYAN,         "╚══════════════════════════════════════════════╝") + C.RESET)
    print(c(C.DIM,  f"  Mode      : {mode}"))
    print(c(C.DIM,  f"  Model     : {model}"))
    if args_dir:
        print(c(C.DIM, f"  Directory : {os.path.abspath(args_dir)}"))
    if iterations:
        print(c(C.DIM, f"  Iterations: {iterations}"))
    print(c(C.CYAN, "  " + "─" * 44))
    print()

def colorize_output(text: str) -> str:
    """Add colours to agent output lines."""
    lines = []
    for line in text.split("\n"):
        if line.startswith("## ✅"):
            lines.append(c(C.GREEN, C.BOLD + line))
        elif line.startswith("## ⚠️"):
            lines.append(c(C.YELLOW, line))
        elif line.startswith("## Iteration") or line.startswith("---"):
            lines.append(c(C.BLUE, line))
        elif line.startswith("### Agent Response"):
            lines.append(c(C.MAGENTA, line))
        elif line.startswith("### Execution Results"):
            lines.append(c(C.CYAN, line))
        elif line.startswith("✅"):
            lines.append(c(C.GREEN, line))
        elif line.startswith("❌"):
            lines.append(c(C.RED, line))
        elif line.startswith("$ "):
            lines.append(c(C.YELLOW, line))
        elif line.startswith("STDOUT:"):
            lines.append(c(C.DIM, line))
        elif line.startswith("STDERR:"):
            lines.append(c(C.RED, line))
        else:
            lines.append(line)
    return "\n".join(lines)

# ── Log file ───────────────────────────────────────────────────────────────────
def save_log(content: str, task: str, logs_dir: str):
    """Save session output to a timestamped log file."""
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_task = "".join(c for c in task[:40] if c.isalnum() or c in " _-").strip().replace(" ", "_")
    filename = os.path.join(logs_dir, f"{timestamp}_{safe_task}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Agent Session Log\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Task:** {task}\n\n---\n\n")
        f.write(content)
    return filename

# ── Chat mode ─────────────────────────────────────────────────────────────────
async def chat_mode(agent, file_tools, shell_tools, logs_dir):
    """Interactive chat loop with the agent."""
    print(c(C.CYAN,   "  💬 Chat mode — type your task or question."))
    print(c(C.DIM,    "  Commands: 'exit' to quit, 'clear' to reset history"))
    print(c(C.CYAN,   "  " + "─" * 44))
    print()

    history = []
    session_log = []
    session_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    while True:
        try:
            user_input = input(c(C.BOLD, "You: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print(c(C.YELLOW, "\n\n  Goodbye!"))
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print(c(C.YELLOW, "\n  Goodbye!"))
            break

        if user_input.lower() == "clear":
            history.clear()
            print(c(C.DIM, "  [History cleared]\n"))
            continue

        # Check if it's a coding task (run autonomous) or a question (chat)
        coding_keywords = ["create", "build", "write", "make", "fix", "add", "generate", "implement", "code"]
        is_coding_task = any(kw in user_input.lower() for kw in coding_keywords)

        session_log.append(f"**You:** {user_input}\n")

        if is_coding_task:
            print(c(C.MAGENTA, f"\n  🚀 Running as autonomous task...\n"))
            result = await agent.run_autonomous(
                task=user_input,
                working_dir="./workspace",
                max_iterations=5,
                file_tools=file_tools,
                shell_tools=shell_tools,
            )
            print(colorize_output(result))
            session_log.append(f"**Agent:**\n{result}\n")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result[:500]})
        else:
            # Plain Q&A using the agent's chat
            print(c(C.MAGENTA, "\n  🤖 Agent: "), end="", flush=True)
            history.append({"role": "user", "content": user_input})
            response = agent._chat(history)
            history.append({"role": "assistant", "content": response})
            print(response)
            session_log.append(f"**Agent:** {response}\n")

        print()

        # Auto-save log after each exchange
        log_content = f"Session started: {session_start}\n\n" + "\n".join(session_log)
        log_path = save_log(log_content, f"chat_session_{session_start[:10]}", logs_dir)

    print(c(C.DIM, f"\n  Session log saved to: {logs_dir}"))

# ── Main ───────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="Groq Autonomous Coding Agent")
    parser.add_argument("task", nargs="?", help="The coding task to perform")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    parser.add_argument("--dir", default="./workspace", help="Working directory (default: ./workspace)")
    parser.add_argument("--iterations", type=int, default=5, help="Max iterations (default: 5)")
    parser.add_argument("--model", default=None, help="Groq model override")
    parser.add_argument("--plan-only", action="store_true", help="Only generate a plan, don't execute")
    parser.add_argument("--logs", default="./logs", help="Directory to save logs (default: ./logs)")
    args = parser.parse_args()

    if not args.chat and not args.task:
        parser.print_help()
        sys.exit(1)

    if not os.environ.get("GROQ_API_KEY"):
        print(c(C.RED, f"\n  ❌ GROQ_API_KEY not found."))
        print(c(C.DIM, f"     Make sure your .env file is at: {os.path.join(BASE_DIR, '.env')}"))
        print(c(C.DIM,  "     And it contains: GROQ_API_KEY=your-key-here\n"))
        sys.exit(1)

    if args.model:
        os.environ["GROQ_MODEL"] = args.model

    model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
    agent = GroqAgent()
    file_tools = FileTools()
    shell_tools = ShellTools()

    # ── Chat mode ──────────────────────────────────────────────────────────────
    if args.chat:
        print_header(None, None, model, mode="chat")
        await chat_mode(agent, file_tools, shell_tools, args.logs)
        return

    # ── Single task mode ───────────────────────────────────────────────────────
    print_header(args.dir, args.iterations, model)
    print(c(C.BOLD, f"  📋 Task: ") + args.task)
    print()
    os.makedirs(args.dir, exist_ok=True)

    if args.plan_only:
        print(c(C.CYAN, "  📝 Generating plan...\n"))
        result = await agent.plan(args.task)
        print(result)
        save_log(result, args.task, args.logs)
    else:
        print(c(C.CYAN, "  🚀 Starting autonomous execution...\n"))
        result = await agent.run_autonomous(
            task=args.task,
            working_dir=args.dir,
            max_iterations=args.iterations,
            file_tools=file_tools,
            shell_tools=shell_tools,
        )
        print(colorize_output(result))
        log_path = save_log(result, args.task, args.logs)
        print(c(C.DIM, f"\n  📄 Log saved to: {log_path}"))

    print(c(C.GREEN, "\n  ✅ Done!\n"))


if __name__ == "__main__":
    asyncio.run(main())