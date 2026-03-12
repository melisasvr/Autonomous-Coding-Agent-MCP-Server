"""
Groq AI Client - Powers the autonomous coding agent loop.
Plan → Code → Test → Fix → Repeat
"""

import logging
import re
import os
import sys
import threading
import itertools
import time

from groq import Groq

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert autonomous coding agent. You plan, write, test, and fix code.

When given a task, you:
1. PLAN: Break it into clear steps
2. CODE: Write clean, working code
3. TEST: Identify what to test
4. FIX: Debug errors with precision

Always respond with valid, executable code when asked to code.
Be concise, practical, and correct.
"""

FIX_PROMPT = """You are a debugging expert. Given broken code and an error, identify the root cause and provide the fixed code.

Format your response as:
## Root Cause
[Brief explanation]

## Fixed Code
```{language}
[fixed code here]
```

## What Changed
[Brief summary of changes]
"""

REVIEW_PROMPT = """You are a senior code reviewer. Review the given code for:
- Bugs and logic errors
- Security issues
- Performance problems
- Code style and readability
- Missing edge case handling

Be specific and actionable in your feedback.
"""

AUTONOMOUS_SYSTEM = """You are a fully autonomous coding agent with access to the filesystem and shell.

CRITICAL RULES — follow these exactly:
1. Use <file path="filename.py"> tags to write files.
2. Use <run> tags to run shell commands — ONE command per <run> block.
3. NEVER output <done> in the same response as <file> or <run> tags.
4. NEVER assume commands succeeded — always wait for actual output before declaring done.
5. After writing files and running commands, STOP and wait for the real output results.
6. Only output <done> when you have SEEN the actual command output confirming success.
7. Keep responses SHORT and focused — write files and run commands, minimal prose.

Workflow per iteration:
- Write files OR run commands (keep it short)
- Wait for real results
- Fix any errors shown in the results
- Only signal <done> after confirming everything works from real output

File write format:
<file path="relative/path/to/file.py">
file content here
</file>

Command format — ONE command per block:
<run>
python script.py
</run>

Signal completion ONLY after seeing successful output:
<done>Summary of what was accomplished</done>
"""


class Spinner:
    """Simple terminal spinner to show the agent is thinking."""
    def __init__(self, message="🤖 Groq is thinking"):
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        for frame in itertools.cycle(frames):
            if not self.running:
                break
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


class GroqAgent:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable not set. "
                "Get your free key at: https://console.groq.com"
            )
        self.client = Groq(api_key=api_key)
        self.model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.request_timeout = int(os.environ.get("GROQ_TIMEOUT", "30"))
        logger.info(f"Groq agent initialized with model: {self.model}")

    def _chat(self, messages: list[dict], system: str = SYSTEM_PROMPT, temperature: float = 0.2) -> str:
        """Send a chat request to Groq with spinner and timeout."""
        spinner = Spinner()
        spinner.start()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}] + messages,
                temperature=temperature,
                max_tokens=2048,        # reduced: faster responses
                timeout=self.request_timeout,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")
        finally:
            spinner.stop()

    async def plan(self, task: str) -> str:
        messages = [
            {
                "role": "user",
                "content": f"Create a detailed step-by-step plan to accomplish this coding task:\n\n{task}\n\nBe specific about files to create, functions to write, and tests to run."
            }
        ]
        return self._chat(messages)

    async def fix_code(self, code: str, error: str, language: str = "python") -> str:
        messages = [
            {
                "role": "user",
                "content": f"Fix this {language} code that has an error.\n\nCode:\n```{language}\n{code}\n```\n\nError:\n```\n{error}\n```"
            }
        ]
        return self._chat(messages, system=FIX_PROMPT)

    async def review_code(self, code: str, context: str = "") -> str:
        context_str = f"\nContext: {context}" if context else ""
        messages = [
            {
                "role": "user",
                "content": f"Review this code:{context_str}\n\n```\n{code}\n```"
            }
        ]
        return self._chat(messages, system=REVIEW_PROMPT)

    async def run_autonomous(
        self,
        task: str,
        working_dir: str,
        max_iterations: int,
        file_tools,
        shell_tools,
    ) -> str:
        """
        Fully autonomous agent loop:
        Plan → Execute (write files / run commands) → Test → Fix → Repeat
        """
        logger.info(f"Starting autonomous task: {task[:80]}...")

        working_dir = os.path.abspath(working_dir)
        os.makedirs(working_dir, exist_ok=True)

        conversation = []
        full_log = [f"# Autonomous Agent Run\n**Task:** {task}\n**Working Dir:** {working_dir}\n"]

        conversation.append({
            "role": "user",
            "content": (
                f"Working directory (absolute): {working_dir}\n\n"
                f"Task: {task}\n\n"
                f"Keep responses SHORT. Write files, run them, verify output, then declare done. "
                f"Do NOT output <done> until you have seen actual successful output."
            )
        })

        for iteration in range(1, max_iterations + 1):
            full_log.append(f"\n---\n## Iteration {iteration}/{max_iterations}\n")
            logger.info(f"Iteration {iteration}/{max_iterations}")

            # Get agent response (with spinner)
            try:
                response = self._chat(conversation, system=AUTONOMOUS_SYSTEM, temperature=0.1)
            except RuntimeError as e:
                msg = f"⚠️ {e}"
                print(f"\n{msg}")
                full_log.append(msg)
                # Ask agent to retry with shorter response
                conversation.append({
                    "role": "user",
                    "content": "Previous request timed out. Please give a SHORT response — just write one file or run one command."
                })
                continue

            conversation.append({"role": "assistant", "content": response})
            full_log.append(f"### Agent Response\n{response}\n")

            # Parse and execute file writes
            file_results = []
            for match in re.finditer(r'<file path="([^"]+)">(.*?)</file>', response, re.DOTALL):
                filepath = match.group(1).strip()
                content = match.group(2).strip()
                full_path = filepath if os.path.isabs(filepath) else os.path.join(working_dir, filepath)
                try:
                    result = file_tools.write_file(full_path, content)
                    file_results.append(f"✅ Wrote {filepath}: {result}")
                    logger.info(f"Wrote file: {full_path}")
                except Exception as e:
                    file_results.append(f"❌ Failed to write {filepath}: {e}")

            # Parse and execute shell commands (one per <run> block, one line at a time)
            command_results = []
            for match in re.finditer(r'<run>(.*?)</run>', response, re.DOTALL):
                for cmd in match.group(1).strip().splitlines():
                    cmd = cmd.strip()
                    if not cmd:
                        continue
                    try:
                        result = shell_tools.run_command(cmd, working_dir=working_dir, timeout=30)
                        command_results.append(f"$ {cmd}\n{result}")
                        logger.info(f"Ran: {cmd[:60]}")
                    except Exception as e:
                        command_results.append(f"$ {cmd}\nERROR: {e}")

            # Feed results back if any actions taken
            if file_results or command_results:
                feedback_parts = []
                if file_results:
                    feedback_parts.append("**File operations:**\n" + "\n".join(file_results))
                if command_results:
                    feedback_parts.append("**Command results:**\n" + "\n".join(command_results))

                feedback = "\n\n".join(feedback_parts)
                full_log.append(f"### Execution Results\n{feedback}\n")

                done_match = re.search(r'<done>(.*?)</done>', response, re.DOTALL)
                all_succeeded = all("✅" in r for r in command_results) if command_results else True

                if done_match and all_succeeded:
                    summary = done_match.group(1).strip()
                    full_log.append(f"\n## ✅ Task Complete\n{summary}")
                    break

                conversation.append({
                    "role": "user",
                    "content": (
                        f"Results:\n\n{feedback}\n\n"
                        f"If everything works, output <done>summary</done>. "
                        f"If there are errors, fix them with a SHORT response."
                    )
                })

            else:
                done_match = re.search(r'<done>(.*?)</done>', response, re.DOTALL)
                if done_match:
                    summary = done_match.group(1).strip()
                    full_log.append(f"\n## ✅ Task Complete\n{summary}")
                    break

                conversation.append({
                    "role": "user",
                    "content": (
                        "No actions detected. Write a file using <file path='...'> "
                        "or run a command using <run>. Keep it short."
                    )
                })

        else:
            full_log.append(f"\n## ⚠️ Max iterations ({max_iterations}) reached")

        return "\n".join(full_log)