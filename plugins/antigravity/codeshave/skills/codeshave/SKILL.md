---
name: codeshave
description: High-speed AST & structural code compressor. Use this skill or type /codeshave whenever the user asks to analyze, explore, summarize, or debug large files or codebases to save 80-95% tokens using the codeshave MCP server.
---

# CodeShave Context Compressor Skill

When this skill is activated (via `/codeshave` or natural prompt):

1. **Always use the `codeshave` MCP server**:
   - For files on disk: Call `shave_file(file_path: "...")` instead of `read_file`.
   - For raw code in memory: Call `shave_code(source_code: "...")`.
2. **Review the compressed AST skeleton**:
   - The skeleton contains 100% of the class structures, method signatures, arguments, type annotations, and docstrings with internal execution loops stripped.
3. **Surgical Follow-up**:
   - Once the target method or line range is identified, read *only* those specific lines if an edit is needed.
