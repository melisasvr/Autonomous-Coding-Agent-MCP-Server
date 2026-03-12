# 🤖 Autonomous Coding Agent — MCP Server
- A fully autonomous coding agent that runs from your terminal in VS Code.  
- It uses **Groq's free API** (LLaMA 3 model) to plan, write, run, and fix code on your behalf — no paid subscription required.
- You give it a task in plain English, and it handles the rest.

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🧠 | **Plan** | Breaks any task into clear, executable steps |
| 💻 | **Code** | Writes files autonomously into your project folder |
| 🔧 | **Test** | Runs your code and captures real output |
| 🐛 | **Fix** | Reads errors and patches the code automatically |
| 💬 | **Chat mode** | Interactive Q&A and task mode in one interface |
| 📄 | **Auto-logs** | Saves every session as a Markdown log file |
| 🎨 | **Colors** | Green = success · Red = error · Yellow = commands |

---

## 📁 Project Structure

```
Autonomous Coding Agent-MCP Server/
├── .env                  ← your Groq API key (keep this private!)
├── .gitignore
├── run_agent.py          ← main entry point
├── server.py             ← MCP server
├── requirements.txt
├── agent/
│   └── groq_client.py   ← Groq AI + autonomous loop
├── tools/
│   ├── file_tools.py    ← read / write / list files
│   ├── shell_tools.py   ← run commands + tests
│   └── code_tools.py    ← syntax check and lint
├── tests/
│   └── test_tools.py    ← pytest test suite
├── logs/                ← auto-saved session logs
└── workspace/           ← agent output files
```

---

## 🚀 Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Get a free Groq API key**  
Go to [https://console.groq.com](https://console.groq.com) — no credit card needed.

**3. Add your key to the `.env` file**
```
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.1-8b-instant
```

---

## 💻 How to Use

**Run a task:**
```bash
python run_agent.py "Create a hello world script" --dir ./workspace
python run_agent.py "Build a calculator" --dir ./calculator
python run_agent.py "Write a password generator" --dir ./workspace
```

**Chat mode — talk to the agent interactively:**
```bash
python run_agent.py --chat
```
Type any question or coding task. Type `exit` to quit, `clear` to reset history.

**Plan only — see the steps without executing:**
```bash
python run_agent.py "Build a todo app" --plan-only
```

---

## ⚙️ Command Reference

| Flag | Description |
|---|---|
| `--dir ./folder` | Set working directory for output files |
| `--iterations N` | Max plan-code-test-fix loops (default: 5) |
| `--model NAME` | Override Groq model |
| `--plan-only` | Generate a plan without executing |
| `--chat` | Start interactive chat mode |
| `--logs ./folder` | Custom folder for session log files |

---

## 🧠 Available Groq Models (Free Tier)

| Model | Best For |
|---|---|
| `llama-3.1-8b-instant` | ⚡ Fast — recommended for most tasks (default) |
| `llama-3.3-70b-versatile` | 🧠 Smarter — use `--model` flag, slower on free tier |
| `mixtral-8x7b-32768` | 🔀 Good for longer code generation tasks |

---

## 💡 Tips

- Use `llama-3.1-8b-instant` (the default) — fastest on the free tier
- Keep tasks specific — `"Create a password generator"` works better than `"Build something"`
- Use `--plan-only` first for complex tasks to preview what the agent will do
- Check the `logs/` folder after each run — every session is saved automatically
- Use `--iterations 8` for complex multi-file projects

---

## 🔒 Safety
- Only writes files inside your home directory and `/tmp`
- Blocks dangerous shell commands like `rm -rf /`
- All commands have a 30 second timeout
- API key is stored in `.env` and never committed to Git

## 🤝 Contributing
- Contributions are welcome and appreciated! Here's how to get involved:
- 🐛 Reporting Bugs
- Check the Issues page to see if it's already reported
- Open a new issue with:
- A clear title and description
- Steps to reproduce
- Expected vs actual behaviour
- Your Python version and OS
- 💡 Suggesting Features
- Open an issue with the enhancement label and describe:
- The problem you're trying to solve
- Your proposed solution
- Why would it benefit other users
- 🔧 Submitting Pull Requests
1. Fork the repository
2. Create a feature branch
- `git checkout -b feature/your-feature-name`
3. Test your changes thoroughly
4. Push to your fork
- `git push origin feature/your-feature-name`

## 📜 License
```
MIT License

Copyright (c) 2026 Deep Research Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including, without limitation, the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
---

*Built by Melis · Powered by Groq Free API · LLaMA 3*
