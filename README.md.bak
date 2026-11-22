# CodeShave

<!-- mcp-name: io.github.jaideepkrishna2008-ui/codeshave -->

<p align="center">
  <img src="assets/banner.svg" alt="CodeShave Banner" width="100%">
</p>

<p align="center">
  <a href="https://pypi.org/project/codeshave/"><img src="https://img.shields.io/pypi/v/codeshave.svg?color=blue&style=flat-square" alt="PyPI" /></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=jaks-360.codeshave"><img src="https://img.shields.io/visual-studio-marketplace/v/jaks-360.codeshave?color=purple&style=flat-square&logo=visual-studio-code&logoColor=white" alt="VS Marketplace" /></a>
  <a href="https://open-vsx.org/extension/jaks-360/codeshave"><img src="https://img.shields.io/badge/Open%20VSX-jaks--360.codeshave-9cf?style=flat-square&logo=eclipseide&logoColor=white" alt="Open VSX" /></a>
  <a href="https://registry.modelcontextprotocol.io/"><img src="https://img.shields.io/badge/Official%20MCP%20Registry-Verified-0ea5e9.svg?style=flat-square&logo=anthropic&logoColor=white" alt="MCP Registry" /></a>
  <a href="https://github.com/jaideepkrishna2008-ui/codeshave/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License" /></a>
  <a href="https://jaideepkrishna2008-ui.github.io/codeshave/"><img src="https://img.shields.io/badge/🌐%20Playground-Live%20Demo-0284c7?style=flat-square" alt="Live Demo" /></a>
</p>

<p align="center">
  <b>High-speed AST & structural code compressor for AI coding assistants and LLMs.</b><br>
  Reduces prompt context by <b>80% to 95%</b> across all major programming languages while preserving 100% valid syntax, type signatures, interfaces, and class hierarchies.<br>
  Eliminates <i>lost-in-the-middle</i> attention dilution and boosts response speeds by up to 10x.
</p>

---

## ⚡ Quick Install

### 1. IDE Extensions (VS Code, Cursor, Antigravity, Windsurf)

- **VS Code & Cursor**: Search for **`CodeShave`** in the Extensions Marketplace (`Ctrl+Shift+X` / `Cmd+Shift+X`) and click **Install**.
  ```bash
  code --install-extension jaks-360.codeshave
  ```
- **Antigravity IDE & Windsurf**: Available via Open VSX Registry as `jaks-360.codeshave`.

### 2. Universal Auto-Connector (CLI & MCP)

Connect to **all** detected assistants (Claude Desktop, Claude Code, Cursor, Windsurf, Antigravity, VS Code) in one command:

```bash
pip install codeshave
codeshave connect --all
```

Or run instantly without installation using `uvx`:

```bash
uvx codeshave mcp
```

---

## 🎯 Key Advantages

| Feature | What It Does | Why It Matters |
| :--- | :--- | :--- |
| **AST Tree Pruning** | Strips function and method bodies into `...` or `{ /* ... */ }`. | Keeps syntax 100% valid; models don't choke on broken code. |
| **Zero Attention Dilution** | Replaces verbose loops with structural declarations. | AI focuses on interfaces and classes rather than implementation noise. |
| **Hallucination Prevention** | Retains all types, annotations, docstrings, and signatures. | The model references exact, verified API contracts instead of guessing. |
| **10x Faster TTFT** | Compresses a 250k-token repository into a 15k skeleton in ~150ms. | Model starts generating intelligent responses almost instantaneously. |
| **Token Budget Enforcer** | Auto-prunes and prioritizes files to fit `--budget 32000`. | Never hit context limits or rate throttles mid-conversation. |

---

## 🌐 Language Support

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

## 🤖 AI Assistant Integration

### 1-Click Auto Configuration
```bash
codeshave connect claude      # Claude Desktop & Claude Code
codeshave connect cursor      # Cursor IDE
codeshave connect windsurf    # Windsurf
codeshave connect antigravity # Google Antigravity
codeshave connect vscode      # VS Code Copilot / Cline
```

### Manual MCP Setup
Add to your assistant's `mcpServers` configuration:
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

### Triggering in Chat
- **Cursor**: Type `@codeshave` in Composer or chat.
- **Windsurf**: Type `@codeshave` in Cascade.
- **Google Antigravity**: Use the `/codeshave` slash command.
- **Hands-Free Automation**: Add a 1-line rule to `.cursorrules`, `.windsurfrules`, or `GEMINI.md`:
  > *"Always invoke the `codeshave` MCP tool (`shave_file` or `shave_code`) when analyzing or exploring codebase architecture."*

---

## 📊 Benchmark Token Savings

Tested across real-world open-source production modules:

| Language & Scope | Original Tokens | CodeShave Skeleton | Reduction |
| :--- | :--- | :--- | :--- |
| **Python** (FastAPI backend + Pydantic models) | 134,069 t | 15,393 t | **88.5%** |
| **TypeScript** (Next.js full-stack services) | 12,450 t | 2,180 t | **82.5%** |
| **Go** (Distributed microservice & gRPC) | 8,920 t | 1,420 t | **84.1%** |
| **Rust** (Compiler engine & AST parser) | 14,200 t | 2,450 t | **82.7%** |
| **Java** (Spring Boot enterprise API) | 18,300 t | 3,100 t | **83.1%** |
| **C++** (High-performance algorithms) | 11,500 t | 2,050 t | **82.2%** |

---

## 🐍 Python SDK

```python
from codeshave import compress_code, compute_savings

source = open("PaymentService.ts").read()
skeleton = compress_code(source, filename_or_ext="PaymentService.ts")
report = compute_savings(source, skeleton)

print(skeleton)
print(report.summary_line())
# -> Original: 4,520 tokens | Skeleton: 790 tokens | Saved: 3,730 tokens (-82.5%)
```

---

## 📄 License & Community

- **Author**: [Jaideep Krishna A](https://github.com/jaideepkrishna2008-ui)
- **License**: [MIT](LICENSE)
- **Official MCP Listing**: [`io.github.jaideepkrishna2008-ui/codeshave`](https://registry.modelcontextprotocol.io/)
- **Live Playground**: [jaideepkrishna2008-ui.github.io/codeshave](https://jaideepkrishna2008-ui.github.io/codeshave/)
