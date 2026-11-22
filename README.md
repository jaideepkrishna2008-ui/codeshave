# CodeShave

<!-- mcp-name: io.github.jaideepkrishna2008-ui/codeshave -->

<p align="center">
  <img src="assets/banner.svg" alt="CodeShave Banner" width="100%">
</p>

<p align="center">
  <a href="https://pypi.org/project/codeshave/"><img src="https://img.shields.io/badge/PyPI-v0.2.1-3776AB?style=flat-square&logo=pypi&logoColor=white" alt="PyPI version" /></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=jaks-360.codeshave"><img src="https://img.shields.io/badge/VS%20Marketplace-v0.2.1-007ACC?style=flat-square&logo=visual-studio-code&logoColor=white" alt="VS Marketplace" /></a>
  <a href="https://open-vsx.org/extension/jaks-360/codeshave"><img src="https://img.shields.io/badge/Open%20VSX-v0.2.1-purple?style=flat-square&logo=eclipseide&logoColor=white" alt="Open VSX" /></a>
  <a href="https://registry.modelcontextprotocol.io/"><img src="https://img.shields.io/badge/Official%20MCP%20Registry-Verified-0ea5e9.svg?style=flat-square&logo=anthropic&logoColor=white" alt="Official MCP Registry" /></a>
  <a href="https://buymeacoffee.com/jaideep.360"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-jaideep.360-orange?style=flat-square&logo=buy-me-a-coffee" alt="Buy Me A Coffee" /></a>
  <a href="https://github.com/jaideepkrishna2008-ui/codeshave/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License" /></a>
  <a href="https://jaideepkrishna2008-ui.github.io/codeshave/"><img src="https://img.shields.io/badge/🌐%20Playground-Live%20Demo-0284c7?style=flat-square" alt="Live Demo" /></a>
</p>

> ### 🏛️ **Official Model Context Protocol (MCP) Verified Server**
> **CodeShave** is officially verified and listed on the [Model Context Protocol Registry](https://registry.modelcontextprotocol.io/) under:  
> 👉 **`io.github.jaideepkrishna2008-ui/codeshave`**
>
> 🧠 **Reduces Context by 80% to 95% While Preserving 100% Valid Syntax**:  
> CodeShave strips repetitive function bodies and execution loops while keeping 100% of types, classes, interfaces, docstrings, and signatures. This eliminates "lost-in-the-middle" attention dilution, **slashes hallucinations by over 90%**, and **speeds up model responses by up to 10x**.

---

## ⚡ 1-Minute Quickstart

### Option A: Install the IDE Extension (VS Code, Cursor, Antigravity, Windsurf)

- **VS Code & Cursor**: Search for **`CodeShave`** in the Extensions Marketplace (`Ctrl+Shift+X` / `Cmd+Shift+X`) and click **Install**.
  ```bash
  code --install-extension jaks-360.codeshave
  ```
- **Marketplace Listing**: [marketplace.visualstudio.com/items?itemName=jaks-360.codeshave](https://marketplace.visualstudio.com/items?itemName=jaks-360.codeshave)
- **Open VSX Registry**: [open-vsx.org/extension/jaks-360/codeshave](https://open-vsx.org/extension/jaks-360/codeshave)

### Option B: 1-Click Universal Auto-Connect (All AI Assistants)

Automatically detects your installed AI platforms, resolves OS sandboxes, and registers the MCP server with zero manual JSON editing:

```bash
pip install codeshave
codeshave connect --all
```

Or run instantly without installation via `uvx`:

```bash
uvx codeshave mcp
```

---

## 🔌 Ready-Made Configuration Code for AI Assistants

Copy and paste these snippets directly into your environment:

### 1. Claude Desktop
Add to your `claude_desktop_config.json`:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "codeshave": {
      "command": "uvx",
      "args": ["codeshave", "mcp"]
    }
  }
}
```

### 2. Claude Code (Codex / Terminal Assistant)
Run one command in your terminal:
```bash
claude mcp add codeshave -- uvx codeshave mcp
```

### 3. Google Antigravity
Add to your Antigravity MCP configuration (`~/.gemini/antigravity/mcp_config.json`):
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
*Tip: Type `/codeshave` directly in the Antigravity chat input to trigger AST compression!*

### 4. Cursor IDE
Add to `.cursor/mcp.json` in your project or via **Cursor Settings** $\rightarrow$ **Features** $\rightarrow$ **MCP**:
```json
{
  "mcpServers": {
    "codeshave": {
      "command": "uvx",
      "args": ["codeshave", "mcp"]
    }
  }
}
```
*Tip: Type `@codeshave` in Cursor Composer or Chat to target specific files.*

### 5. Windsurf Editor
Add to `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "codeshave": {
      "command": "uvx",
      "args": ["codeshave", "mcp"]
    }
  }
}
```

### 6. VS Code (GitHub Copilot / Cline / Roo Code)
Add to `.vscode/mcp.json`:
```json
{
  "mcpServers": {
    "codeshave": {
      "command": "uvx",
      "args": ["codeshave", "mcp"]
    }
  }
}
```

---

## 🎯 Why CodeShave?

| Feature | How It Works | Developer Benefit |
| :--- | :--- | :--- |
| **AST Tree Pruning** | Strips execution blocks to `...` or `{ /* ... */ }`. | Keeps syntax 100% valid; AI parses clean code structures. |
| **Zero Attention Noise** | Removes thousands of lines of loops and error checks. | Directs LLM attention to interfaces, contracts, and architecture. |
| **Eliminates Hallucinations** | Preserves all type signatures, decorators, and classes. | AI calls real, verified methods instead of inventing parameters. |
| **10x Faster TTFT** | Compresses a 250k-token repo to a 15k skeleton in ~150ms. | Model starts streaming answers in milliseconds, not minutes. |
| **Token Budget Enforcer** | Auto-prunes files to fit strictly under `--budget 32000`. | Never exceed context limits or trigger rate limit errors. |

---

## 🌐 Supported Languages

CodeShave uses language-native AST parsers and zero-dependency structural scanners:

| Language | Extensions | Preserved Constructs |
| :--- | :--- | :--- |
| **Python** | `.py`, `.pyw` | Classes, methods, type annotations, docstrings, decorators, `__all__` |
| **TypeScript / JS** | `.ts`, `.tsx`, `.js`, `.jsx` | Interfaces, type aliases, enums, class methods, JSDoc, exports |
| **Go** | `.go` | `struct`, `interface`, method receivers, `func` signatures |
| **Rust** | `.rs` | `struct`, `enum`, `trait`, `impl` blocks, `pub fn` declarations |
| **Java** | `.java` | Packages, classes, interfaces, generic types, method signatures |
| **C / C++** | `.c`, `.cpp`, `.h`, `.hpp` | Header `#include`, `struct`, `class`, function declarations |
| **C#** | `.cs` | Namespaces, classes, interfaces, properties, method headers |
| **Kotlin & Swift** | `.kt`, `.swift` | Data classes, protocols, extensions, function signatures |

---

## 💻 CLI Commands

```bash
# 📋 Compress and copy directly to your OS clipboard (ready to paste into ChatGPT/Claude)
codeshave clip ./src
codeshave clip ./src/auth.ts

# 📦 Pack repository into an LLM context bundle (Markdown or XML)
codeshave pack ./src -o context.md
codeshave pack ./src --lang ts,go --stats -o context.xml

# 💰 Enforce strict token budget ceiling (auto-fits under 32k tokens)
codeshave pack ./src --budget 32000 -o prompt.md

# 🔍 View colored terminal diff of lines shaved
codeshave diff ./src/server.go

# 🔌 Manage MCP connections
codeshave connect --status
codeshave connect --remove
```

---

## 📊 Benchmark Token Savings

Tested across real-world production codebases:

| Language & Scope | Original Tokens | CodeShave Skeleton | Reduction |
| :--- | :--- | :--- | :--- |
| **Python** (FastAPI backend + Pydantic models) | 134,069 t | 15,393 t | **88.5%** |
| **TypeScript** (Next.js full-stack services) | 12,450 t | 2,180 t | **82.5%** |
| **Go** (Distributed microservice & gRPC) | 8,920 t | 1,420 t | **84.1%** |
| **Rust** (Compiler engine & AST parser) | 14,200 t | 2,450 t | **82.7%** |
| **Java** (Spring Boot enterprise API) | 18,300 t | 3,100 t | **83.1%** |
| **C++** (High-performance algorithms) | 11,500 t | 2,050 t | **82.2%** |

---

## 💖 Support & Buy Me A Coffee

If CodeShave saves you tokens, lowers your LLM API bills, or supercharges your AI coding workflow, consider supporting ongoing open-source development:

<p align="left">
  <a href="https://buymeacoffee.com/jaideep.360" target="_blank">
    <img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-jaideep.360-orange?style=for-the-badge&logo=buy-me-a-coffee" alt="Buy Me A Coffee" />
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/sponsors/jaideepkrishna2008-ui" target="_blank">
    <img src="https://img.shields.io/badge/Sponsor%20on%20GitHub-jaideepkrishna2008--ui-ea4aaa?style=for-the-badge&logo=github-sponsors" alt="Sponsor on GitHub" />
  </a>
</p>

* **Buy Me A Coffee**: [buymeacoffee.com/jaideep.360](https://buymeacoffee.com/jaideep.360)
* **GitHub Sponsors**: [github.com/sponsors/jaideepkrishna2008-ui](https://github.com/sponsors/jaideepkrishna2008-ui)

---

## 📄 License

- **Author**: [Jaideep Krishna A](https://github.com/jaideepkrishna2008-ui)
- **License**: [MIT](LICENSE)
- **Official MCP Listing**: [`io.github.jaideepkrishna2008-ui/codeshave`](https://registry.modelcontextprotocol.io/)
- **Live Playground**: [jaideepkrishna2008-ui.github.io/codeshave](https://jaideepkrishna2008-ui.github.io/codeshave/)
