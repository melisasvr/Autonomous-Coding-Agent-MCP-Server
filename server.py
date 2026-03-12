"""
Autonomous Coding Agent MCP Server - Powered by Groq
Provides tools for: planning, coding, testing, and fixing code autonomously.
"""

import asyncio
import json
import logging
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from agent.groq_client import GroqAgent
from tools.file_tools import FileTools
from tools.shell_tools import ShellTools
from tools.code_tools import CodeTools

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

app = Server("groq-coding-agent")

# Initialize tools
file_tools = FileTools()
shell_tools = ShellTools()
code_tools = CodeTools()
groq_agent = GroqAgent()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="agent_run",
            description=(
                "Autonomous coding agent: given a task, it plans, writes code, "
                "runs tests, and fixes errors using Groq AI. "
                "Use this for any coding task end-to-end."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The coding task to complete autonomously"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory for the task (default: current dir)",
                        "default": "."
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "Max plan-code-test-fix iterations (default: 5)",
                        "default": 5
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="agent_plan",
            description="Ask Groq to create a step-by-step plan for a coding task without executing it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task to plan for"}
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="agent_fix",
            description="Given code and an error message, ask Groq to diagnose and fix it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The broken code"},
                    "error": {"type": "string", "description": "The error message"},
                    "language": {"type": "string", "description": "Programming language", "default": "python"}
                },
                "required": ["code", "error"]
            }
        ),
        Tool(
            name="agent_review",
            description="Ask Groq to review code for bugs, style, and improvements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Code to review"},
                    "context": {"type": "string", "description": "What the code is supposed to do"}
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="read_file",
            description="Read a file from disk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file on disk.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_files",
            description="List files in a directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory to list", "default": "."}
                }
            }
        ),
        Tool(
            name="run_command",
            description="Run a shell command and return stdout/stderr.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"},
                    "working_dir": {"type": "string", "description": "Working directory", "default": "."},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="run_tests",
            description="Run Python tests (pytest) in a directory and return results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory with tests", "default": "."},
                    "test_file": {"type": "string", "description": "Specific test file (optional)"}
                }
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "agent_run":
            result = await groq_agent.run_autonomous(
                task=arguments["task"],
                working_dir=arguments.get("working_dir", "."),
                max_iterations=arguments.get("max_iterations", 5),
                file_tools=file_tools,
                shell_tools=shell_tools,
            )
            return [TextContent(type="text", text=result)]

        elif name == "agent_plan":
            result = await groq_agent.plan(arguments["task"])
            return [TextContent(type="text", text=result)]

        elif name == "agent_fix":
            result = await groq_agent.fix_code(
                code=arguments["code"],
                error=arguments["error"],
                language=arguments.get("language", "python")
            )
            return [TextContent(type="text", text=result)]

        elif name == "agent_review":
            result = await groq_agent.review_code(
                code=arguments["code"],
                context=arguments.get("context", "")
            )
            return [TextContent(type="text", text=result)]

        elif name == "read_file":
            result = file_tools.read_file(arguments["path"])
            return [TextContent(type="text", text=result)]

        elif name == "write_file":
            result = file_tools.write_file(arguments["path"], arguments["content"])
            return [TextContent(type="text", text=result)]

        elif name == "list_files":
            result = file_tools.list_files(arguments.get("directory", "."))
            return [TextContent(type="text", text=result)]

        elif name == "run_command":
            result = shell_tools.run_command(
                command=arguments["command"],
                working_dir=arguments.get("working_dir", "."),
                timeout=arguments.get("timeout", 30)
            )
            return [TextContent(type="text", text=result)]

        elif name == "run_tests":
            result = shell_tools.run_tests(
                directory=arguments.get("directory", "."),
                test_file=arguments.get("test_file")
            )
            return [TextContent(type="text", text=result)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool {name} error: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error in {name}: {str(e)}")]


async def main():
    logger.info("Starting Groq Autonomous Coding Agent MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())