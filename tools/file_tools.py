"""
File Tools - Read, write, list files safely.
"""

import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Safety: never allow writing outside these base paths
SAFE_WRITE_ROOTS = [
    os.path.expanduser("~"),
    "/tmp",
    "/home",
]


class FileTools:
    def _is_safe_path(self, path: str) -> bool:
        """Check if path is within safe write roots."""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(root) for root in SAFE_WRITE_ROOTS)

    def read_file(self, path: str) -> str:
        """Read a file and return its contents."""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return f"Error: File not found: {path}"
            
            size = os.path.getsize(path)
            if size > 1_000_000:  # 1MB limit
                return f"Error: File too large ({size} bytes). Max 1MB."
            
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            lines = content.count("\n") + 1
            return f"# File: {path} ({lines} lines)\n\n{content}"
        
        except PermissionError:
            return f"Error: Permission denied reading {path}"
        except Exception as e:
            return f"Error reading {path}: {e}"

    def write_file(self, path: str, content: str) -> str:
        """Write content to a file, creating directories as needed."""
        try:
            path = os.path.expanduser(path)
            
            if not self._is_safe_path(path):
                return f"Error: Path {path} is outside safe write roots. Refusing to write."
            
            # Create parent directories
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            size = os.path.getsize(path)
            lines = content.count("\n") + 1
            return f"Successfully wrote {path} ({lines} lines, {size} bytes)"
        
        except PermissionError:
            return f"Error: Permission denied writing {path}"
        except Exception as e:
            return f"Error writing {path}: {e}"

    def list_files(self, directory: str = ".") -> str:
        """List files in a directory (recursive, up to 2 levels)."""
        try:
            directory = os.path.expanduser(directory)
            if not os.path.exists(directory):
                return f"Error: Directory not found: {directory}"
            
            if not os.path.isdir(directory):
                return f"Error: {directory} is not a directory"
            
            results = []
            results.append(f"📁 {os.path.abspath(directory)}")
            
            for root, dirs, files in os.walk(directory):
                # Limit depth
                depth = root.replace(directory, "").count(os.sep)
                if depth >= 3:
                    dirs.clear()
                    continue
                
                # Skip hidden and common ignore dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in 
                           {"__pycache__", "node_modules", ".git", "venv", ".venv", "dist", "build"}]
                
                indent = "  " * depth
                rel_root = os.path.relpath(root, directory)
                
                if rel_root != ".":
                    results.append(f"{indent}📁 {os.path.basename(root)}/")
                
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    size_str = f"{size}B" if size < 1024 else f"{size//1024}KB"
                    results.append(f"{indent}  📄 {file} ({size_str})")
            
            if len(results) == 1:
                results.append("  (empty directory)")
            
            return "\n".join(results)
        
        except Exception as e:
            return f"Error listing {directory}: {e}"

    def append_file(self, path: str, content: str) -> str:
        """Append content to an existing file."""
        try:
            path = os.path.expanduser(path)
            if not self._is_safe_path(path):
                return f"Error: Path {path} is outside safe write roots."
            
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"Appended {len(content)} chars to {path}"
        except Exception as e:
            return f"Error appending to {path}: {e}"