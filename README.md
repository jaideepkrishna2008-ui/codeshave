# CodeShave

<p align="center">
  <img src="assets/banner.svg" alt="CodeShave Banner" width="100%">
</p>

<p align="center">
  <b>High-speed, deterministic AST code context compressor for AI coding assistants and local LLMs.</b><br>
  Reduces prompt tokens by 60% to 80% while preserving valid syntax, type signatures, and class hierarchies.
</p>

---

## ⚡ Terminal Demo

<p align="center">
  <img src="assets/demo.svg" alt="CodeShave CLI Demonstration" width="100%">
</p>

---

## 🎯 Why CodeShave?

When developers feed large directories to LLMs or AI agents, context windows quickly fill up, latency spikes, and API token bills mount. 

Traditional approaches either:
1. Truncate files blindly, breaking syntax trees and references.
2. Rely on costly, slow LLMs to summarize code before prompting.

**CodeShave** uses Python's native Abstract Syntax Tree (AST) engine to deterministically transform code into clean interface skeletons:
- Strips implementation logic inside functions and replaces with `...`.
- Preserves all class structures, inheritance, and attributes.
- Retains parameter type annotations, defaults, and return types.
- Maintains decorators, docstrings, and module-level exports.
- Formats context blocks into Markdown, Claude-optimized XML, or JSON.

---

## 🏗️ Architecture

<p align="center">
  <img src="assets/architecture.svg" alt="CodeShave Architecture Diagram" width="100%">
</p>

---

## 🚀 Quickstart

### Installation

Install directly via `pip` from GitHub:

```bash
pip install git+https://github.com/jaideepkrishna2008-ui/codeshave.git
```

Or clone for local development:

```bash
git clone https://github.com/jaideepkrishna2008-ui/codeshave.git
cd codeshave
pip install -e .
```

### ⚡ CLI Commands

```bash
# 📋 One-Click Clipboard Copy: Compress and copy directly to clipboard
codeshave clip ./src
codeshave clip ./src/models.py
# -> Copied to clipboard! Ready to paste directly into ChatGPT, Claude, or Cursor!

# 📦 Pack directory into an LLM context bundle
codeshave pack ./src -o llm_context.md

# 🏷️ Generate Claude-optimized XML bundle with live savings statistics
codeshave pack ./src --format xml --stats -o llm_context.xml

# 🔍 Inspect a single file's compressed skeleton
codeshave inspect ./src/services/billing.py
```

---

## 🔌 Model Context Protocol (MCP) Integration

CodeShave runs as a turnkey **MCP Server** over standard I/O, allowing **Claude Desktop**, **Cursor**, and **Windsurf** to automatically compress files on the fly before reasoning:

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "codeshave": {
      "command": "codeshave",
      "args": ["mcp"]
    }
  }
}
```

### Python API

```python
from codeshave import compress_source, compute_savings

raw_code = open("service.py").read()
skeleton = compress_source(raw_code, preserve_docstrings=True)
report = compute_savings(raw_code, skeleton)

print(skeleton)
print(report.summary_line())
```

---

## 📊 Token Savings Benchmark

| Source Type | Original Tokens | CodeShave Skeleton | Reduction | Syntax Status |
| :--- | :--- | :--- | :--- | :--- |
| Data Models | 3,460 t | 920 t | **73.4%** | ✅ Valid AST |
| API Endpoints | 4,210 t | 780 t | **81.5%** | ✅ Valid AST |
| Business Logic | 6,840 t | 1,120 t | **83.6%** | ✅ Valid AST |
| Utility Scripts | 1,000 t | 400 t | **60.0%** | ✅ Valid AST |

---

## 💖 Sponsorship & Backing

If CodeShave saves you tokens, reduces your API bills, or accelerates your agent workflow, consider supporting ongoing open-source development:

<p align="left">
  <a href="https://buymeacoffee.com/jaideep.360" target="_blank">
    <img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-jaideep.360-orange?style=for-the-badge&logo=buy-me-a-coffee" alt="Buy Me A Coffee" />
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/sponsors/jaideepkrishna2008-ui" target="_blank">
    <img src="https://img.shields.io/badge/Sponsor%20on%20GitHub-jaideepkrishna2008--ui-ea4aaa?style=for-the-badge&logo=github-sponsors" alt="Sponsor on GitHub" />
  </a>
</p>

* **Buy Me A Coffee**: [https://buymeacoffee.com/jaideep.360](https://buymeacoffee.com/jaideep.360)
* **GitHub Sponsors**: [https://github.com/sponsors/jaideepkrishna2008-ui](https://github.com/sponsors/jaideepkrishna2008-ui)

---

## 📄 License

Created by **Jaideep Krishna A** ([@jaideepkrishna2008-ui](https://github.com/jaideepkrishna2008-ui)).
Licensed under the Apache License 2.0 or MIT equivalent open-source terms.
