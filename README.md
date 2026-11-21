# CodeShave

<p align="center">
  <img src="assets/banner.svg" alt="CodeShave Banner" width="100%">
</p>

<p align="center">
  <a href="https://pypi.org/project/codeshave/"><img src="https://img.shields.io/pypi/v/codeshave.svg?color=blue&style=flat-square" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/codeshave/"><img src="https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python Versions" /></a>
  <a href="https://github.com/jaideepkrishna2008-ui/codeshave/actions/workflows/ci.yml"><img src="https://github.com/jaideepkrishna2008-ui/codeshave/actions/workflows/ci.yml/badge.svg?style=flat-square" alt="CI Status" /></a>
  <a href="https://buymeacoffee.com/jaideep.360"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-jaideep.360-orange?style=flat-square&logo=buy-me-a-coffee" alt="Buy Me A Coffee" /></a>
</p>

> ### ⚡ **Try CodeShave Live in Your Browser (Zero Install Required)**
> Paste your code and test real-time token reduction across **Python, TypeScript, Go, Rust, Java, C++** right now:  
> 👉 [**https://jaideepkrishna2008-ui.github.io/codeshave/**](https://jaideepkrishna2008-ui.github.io/codeshave/)

<p align="center">
  <b>High-speed, deterministic AST & structural code context compressor for AI coding assistants and LLMs.</b><br>
  Reduces prompt tokens by 60% to 85% across all major programming languages while preserving valid syntax, type signatures, interfaces, and class hierarchies.
</p>

---

## ⚡ Terminal Demo

<p align="center">
  <img src="assets/terminal_recording.gif" alt="CodeShave Live Terminal Demo" width="100%">
</p>

<p align="center">
  <a href="https://jaideepkrishna2008-ui.github.io/codeshave/" target="_blank">
    <img src="https://img.shields.io/badge/🌐%20Try%20Live%20In%20Browser-Playground-0284c7?style=for-the-badge" alt="Live Web Playground" />
  </a>
</p>

---

## 🎯 Why CodeShave?

When developers feed entire codebases to LLMs or AI agents, context windows quickly fill up, latency spikes, and API token bills mount. 

Traditional approaches either:
1. **Truncate files blindly**, breaking syntax trees, references, and imports.
2. **Rely on costly, slow LLMs** to summarize code before prompting.

**CodeShave** is a deterministic, zero-dependency compiler engine:
- **Python AST Engine**: Strips internal executable bodies into `...`, preserving full decorators, types, docstrings, classes, and `__all__`.
- **Universal Multi-Language Engine**: Strips execution loops inside `{ ... }` into `{ /* ... */ }` across TypeScript, JavaScript, Go, Rust, Java, C++, and C# while keeping 100% of interfaces, structs, types, imports, and function signatures intact.
- **Topological Sorting**: Orders files by module dependencies so the LLM reads prerequisite definitions first.
- **Budget Enforcer**: Automatically compresses a repository to fit exactly under your target token limit (e.g. `--budget 32000`).
- **Turnkey MCP Server**: Seamlessly integrates with Claude Desktop, Cursor, Windsurf, and Antigravity.

---

## 🌐 Supported Languages

CodeShave natively supports the world's most popular programming languages out of the box with zero external dependencies:

| Language | Extensions | Compression Engine | Preserved Constructs |
| :--- | :--- | :--- | :--- |
| **Python** | `.py`, `.pyw` | Python Native AST | Classes, methods, docstrings, type annotations, decorators, `__all__` |
| **TypeScript** | `.ts`, `.tsx` | Structural Scanner | Interfaces, `type` aliases, enums, class methods, JSDoc, exports |
| **JavaScript** | `.js`, `.jsx`, `.mjs`, `.cjs` | Structural Scanner | ES6 classes, arrow functions, exported modules, constructor signatures |
| **Go** | `.go` | Structural Scanner | `type Struct struct`, `type Interface interface`, method receivers, `func` |
| **Rust** | `.rs` | Structural Scanner | `struct`, `enum`, `trait`, `impl` blocks, `pub fn` signatures |
| **Java** | `.java` | Structural Scanner | Packages, classes, interfaces, generic types, method signatures |
| **C / C++** | `.c`, `.cpp`, `.h`, `.hpp` | Structural Scanner | Header `#include`, `struct`, `class`, method/function declarations |
| **C#** | `.cs` | Structural Scanner | Namespaces, classes, interfaces, properties, method headers |
| **Kotlin & Scala** | `.kt`, `.scala` | Structural Scanner | Classes, traits, data classes, function signatures |
| **Swift & Dart** | `.swift`, `.dart` | Structural Scanner | Protocols, extensions, classes, functions |
| **PHP** | `.php` | Structural Scanner | Namespaces, classes, interfaces, function signatures |
| **Ruby** | `.rb` | Indentation Scanner | Classes, modules, `def ... end` signatures |
| **Shell / Bash** | `.sh`, `.bash`, `.zsh` | Lexical Scanner | Function headers, environment variables, commands |

---

## 🏗️ Architecture

<p align="center">
  <img src="assets/architecture.svg" alt="CodeShave Architecture Diagram" width="100%">
</p>

---

## 🚀 Quickstart

### Installation

Install globally from PyPI:

```bash
pip install codeshave
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/jaideepkrishna2008-ui/codeshave.git
```

### ⚡ CLI Usage

```bash
# 📋 One-Click Clipboard Copy: Compress and copy directly to OS clipboard
codeshave clip ./src
codeshave clip ./src/service.ts
# -> Copied to clipboard! Ready to paste into ChatGPT, Claude, or Cursor!

# 📦 Pack entire multi-language repository into an LLM context bundle
codeshave pack ./src -o llm_context.md

# 🎯 Filter by language (e.g. only TypeScript and Go)
codeshave pack ./src --lang ts,go -o context.md

# 🏷️ Generate Claude-optimized XML bundle with live savings metrics
codeshave pack ./src --format xml --stats -o llm_context.xml

# 💰 Enforce strict token budget ceiling (auto-prunes to fit under 32k tokens)
codeshave pack ./src --budget 32000 -o prompt_context.md

# 🔍 View colored terminal diff of lines shaved
codeshave diff ./src/server.go

# 📄 Inspect a single file's compressed skeleton
codeshave inspect ./src/services/billing.ts
```

---

## 🔌 AI Assistant & Editor Integration (MCP Server)

CodeShave runs as a turnkey **Model Context Protocol (MCP)** server over standard I/O (`stdio`). This allows AI coding assistants to automatically invoke CodeShave and compress source code before analyzing it, saving up to 85% on prompt tokens.

### 1. Claude Desktop

Add to your `claude_desktop_config.json`:
* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

### 2. Cursor IDE

1. Open **Cursor Settings** $\rightarrow$ **Features** $\rightarrow$ **MCP**.
2. Click **+ Add New MCP Server**.
3. Configure:
   * **Name**: `codeshave`
   * **Type**: `command`
   * **Command**: `codeshave mcp`

Alternatively, add to `.cursor/mcp.json` in your workspace:

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

### 3. Windsurf Editor

Add to `~/.codeium/windsurf/mcp_config.json`:

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

### 4. Google Antigravity

In your Antigravity MCP configuration (`~/.gemini/antigravity/mcp_config.json` or project settings):

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

### 5. Python SDK

```python
from codeshave import compress_code, compute_savings

# Compresses any language (Python, TypeScript, Go, Rust, Java, etc.)
code = open("UserService.ts").read()
skeleton = compress_code(code, filename_or_ext="UserService.ts")
report = compute_savings(code, skeleton)

print(skeleton)
print(report.summary_line())
# -> Original: 4,520 tokens | Skeleton: 790 tokens | Saved: 3,730 tokens (-82.5%)
```

---

## 📊 Token Savings Benchmark

| Source Language | Original Tokens | CodeShave Skeleton | Reduction | Syntax Preservation |
| :--- | :--- | :--- | :--- | :--- |
| **Python** (Data Models & API) | 134,069 t | 15,393 t | **88.5%** | ✅ 100% Valid AST |
| **TypeScript** (React & Services) | 12,450 t | 2,180 t | **82.5%** | ✅ Interfaces & Signatures |
| **Go** (HTTP API & Router) | 8,920 t | 1,420 t | **84.1%** | ✅ Structs & Receivers |
| **Rust** (Engine & Impl) | 14,200 t | 2,450 t | **82.7%** | ✅ Traits & Fn Signatures |
| **Java** (Enterprise Services) | 18,300 t | 3,100 t | **83.1%** | ✅ Classes & Types |
| **C++** (Core Algorithms) | 11,500 t | 2,050 t | **82.2%** | ✅ Headers & Declarations |

---

## 💖 Sponsorship & Backing

If CodeShave saves you tokens, reduces your LLM API bills, or accelerates your AI agent workflow, consider supporting ongoing open-source development:

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
Licensed under the MIT License.
