"""
Tests for file tools, shell tools, and code tools.
Run: pytest tests/ -v
"""

import os
import pytest
import tempfile
from tools.file_tools import FileTools
from tools.shell_tools import ShellTools
from tools.code_tools import CodeTools


# ─── File Tools Tests ──────────────────────────────────────────────────────────

class TestFileTools:
    def setup_method(self):
        self.ft = FileTools()
        self.tmpdir = tempfile.mkdtemp()

    def test_write_and_read_file(self):
        path = os.path.join(self.tmpdir, "test.txt")
        result = self.ft.write_file(path, "hello world")
        assert "Successfully wrote" in result

        content = self.ft.read_file(path)
        assert "hello world" in content

    def test_read_nonexistent_file(self):
        result = self.ft.read_file("/nonexistent/path/file.txt")
        assert "Error" in result or "not found" in result.lower()

    def test_list_files(self):
        # Create some files
        self.ft.write_file(os.path.join(self.tmpdir, "a.py"), "# a")
        self.ft.write_file(os.path.join(self.tmpdir, "b.py"), "# b")

        result = self.ft.list_files(self.tmpdir)
        assert "a.py" in result
        assert "b.py" in result

    def test_write_creates_directories(self):
        path = os.path.join(self.tmpdir, "subdir", "nested", "file.py")
        result = self.ft.write_file(path, "print('hi')")
        assert "Successfully wrote" in result
        assert os.path.exists(path)

    def test_safety_check_blocks_root(self):
        result = self.ft.write_file("/etc/passwd", "hacked")
        assert "Error" in result or "BLOCKED" in result or "safe" in result.lower()


# ─── Shell Tools Tests ──────────────────────────────────────────────────────────

class TestShellTools:
    def setup_method(self):
        self.sh = ShellTools()

    def test_run_simple_command(self):
        result = self.sh.run_command("echo hello")
        assert "hello" in result

    def test_run_python_command(self):
        result = self.sh.run_command("python -c \"print('test ok')\"")
        assert "test ok" in result

    def test_command_failure_captured(self):
        result = self.sh.run_command("python -c \"raise ValueError('boom')\"")
        assert "boom" in result or "ValueError" in result

    def test_blocked_dangerous_command(self):
        result = self.sh.run_command("rm -rf /")
        assert "BLOCKED" in result

    def test_timeout_respected(self):
        result = self.sh.run_command("sleep 10", timeout=1)
        assert "Timeout" in result or "timeout" in result.lower()


# ─── Code Tools Tests ──────────────────────────────────────────────────────────

class TestCodeTools:
    def setup_method(self):
        self.ct = CodeTools()

    def test_valid_python_syntax(self):
        result = self.ct.check_python_syntax("def foo():\n    return 42\n")
        assert "OK" in result or "✅" in result

    def test_invalid_python_syntax(self):
        result = self.ct.check_python_syntax("def foo(\n    return 42")
        assert "Error" in result or "❌" in result

    def test_extract_code_blocks(self):
        text = "Here is code:\n```python\nprint('hi')\n```\nDone."
        blocks = self.ct.extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]["language"] == "python"
        assert "print" in blocks[0]["code"]

    def test_extract_multiple_blocks(self):
        text = "```python\nx = 1\n```\n```bash\necho hi\n```"
        blocks = self.ct.extract_code_blocks(text)
        assert len(blocks) == 2