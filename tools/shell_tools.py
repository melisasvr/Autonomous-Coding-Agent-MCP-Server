"""
Shell Tools - Run commands, tests safely with timeouts.
"""

import subprocess
import os
import shlex
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Commands that are blocked for safety
BLOCKED_COMMANDS = {
    "rm -rf /", "rm -rf ~", "mkfs", "dd if=/dev/zero",
    ":(){ :|:& };:", "chmod -R 777 /", "> /dev/sda",
}

MAX_OUTPUT_CHARS = 8000  # Truncate large outputs


class ShellTools:
    def _is_safe_command(self, command: str) -> tuple[bool, str]:
        """Basic safety check for commands."""
        cmd_lower = command.strip().lower()
        for blocked in BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return False, f"Blocked dangerous command pattern: {blocked}"
        return True, ""

    def run_command(self, command: str, working_dir: str = ".", timeout: int = 30) -> str:
        """Run a shell command and return stdout + stderr."""
        try:
            # Safety check
            safe, reason = self._is_safe_command(command)
            if not safe:
                return f"❌ BLOCKED: {reason}"

            # Expand working dir
            working_dir = os.path.expanduser(working_dir)
            if not os.path.exists(working_dir):
                os.makedirs(working_dir, exist_ok=True)

            logger.info(f"Running: {command[:80]} in {working_dir}")

            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )

            output_parts = []
            
            if result.stdout:
                stdout = result.stdout
                if len(stdout) > MAX_OUTPUT_CHARS:
                    stdout = stdout[:MAX_OUTPUT_CHARS] + f"\n... [truncated, {len(result.stdout)} total chars]"
                output_parts.append(f"STDOUT:\n{stdout}")
            
            if result.stderr:
                stderr = result.stderr
                if len(stderr) > MAX_OUTPUT_CHARS:
                    stderr = stderr[:MAX_OUTPUT_CHARS] + f"\n... [truncated]"
                output_parts.append(f"STDERR:\n{stderr}")

            if not output_parts:
                output_parts.append("(no output)")

            status = "✅" if result.returncode == 0 else f"❌ (exit code {result.returncode})"
            return f"{status} Command: {command}\n" + "\n".join(output_parts)

        except subprocess.TimeoutExpired:
            return f"❌ Timeout ({timeout}s): {command}"
        except Exception as e:
            return f"❌ Error running command: {e}"

    def run_tests(self, directory: str = ".", test_file: str = None) -> str:
        """Run pytest and return structured results."""
        try:
            directory = os.path.expanduser(directory)
            
            if test_file:
                cmd = f"python -m pytest {test_file} -v --tb=short 2>&1"
            else:
                cmd = "python -m pytest . -v --tb=short 2>&1"
            
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            output = result.stdout + result.stderr
            if len(output) > MAX_OUTPUT_CHARS:
                output = output[:MAX_OUTPUT_CHARS] + "\n... [truncated]"
            
            status = "✅ Tests passed" if result.returncode == 0 else "❌ Tests failed"
            return f"{status}\n\n{output}"

        except subprocess.TimeoutExpired:
            return "❌ Tests timed out after 120 seconds"
        except Exception as e:
            return f"❌ Error running tests: {e}"

    def run_python_file(self, filepath: str, args: str = "", working_dir: str = ".") -> str:
        """Run a Python file directly."""
        cmd = f"python {filepath} {args}".strip()
        return self.run_command(cmd, working_dir=working_dir, timeout=30)

    def install_package(self, package: str) -> str:
        """Install a Python package via pip."""
        safe_package = shlex.quote(package)
        cmd = f"pip install {safe_package} --quiet"
        return self.run_command(cmd, timeout=60)