"""
Code Tools - Syntax checking, linting, formatting helpers.
"""

import ast
import subprocess
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


class CodeTools:
    def check_python_syntax(self, code: str) -> str:
        """Check Python code for syntax errors."""
        try:
            ast.parse(code)
            return "✅ Syntax OK"
        except SyntaxError as e:
            return f"❌ Syntax Error at line {e.lineno}: {e.msg}\n  {e.text}"
        except Exception as e:
            return f"❌ Parse error: {e}"

    def extract_code_blocks(self, text: str) -> list[dict]:
        """Extract code blocks from markdown-style text."""
        import re
        blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(pattern, text, re.DOTALL):
            language = match.group(1) or "text"
            code = match.group(2).strip()
            blocks.append({"language": language, "code": code})
        return blocks

    def lint_python(self, code: str) -> str:
        """Run basic flake8 linting on Python code (if available)."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmpfile = f.name

            result = subprocess.run(
                ["python", "-m", "flake8", tmpfile, "--max-line-length=100"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            os.unlink(tmpfile)

            if result.returncode == 0:
                return "✅ No linting issues"
            else:
                # Strip temp file path from output
                output = result.stdout.replace(tmpfile, "<code>")
                return f"⚠️ Linting issues:\n{output}"

        except FileNotFoundError:
            return "ℹ️ flake8 not installed (skipping lint)"
        except Exception as e:
            return f"Lint error: {e}"

    def format_python(self, code: str) -> str:
        """Format Python code with black (if available)."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmpfile = f.name

            result = subprocess.run(
                ["python", "-m", "black", tmpfile, "--quiet"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                with open(tmpfile, "r") as f:
                    formatted = f.read()
                os.unlink(tmpfile)
                return formatted
            else:
                os.unlink(tmpfile)
                return code  # Return original if formatting fails

        except FileNotFoundError:
            return code  # black not installed
        except Exception:
            return code