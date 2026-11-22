# CodeShave Context Efficiency Rules

- **Code Exploration**: Prioritize calling the `codeshave` MCP tool (`shave_file` or `shave_code`) when analyzing, searching, or exploring large source files (>100 lines) across Python, TypeScript, JavaScript, Go, Rust, Java, C++, and C#.
- **Preserved Signal**: CodeShave preserves 100% of class hierarchies, method signatures, argument types, and docstrings while stripping execution loops. Use the compressed skeleton for architecture comprehension before reading specific line ranges.
- **Zero Hallucination**: Never guess function signatures or parameter names; inspect the CodeShave skeleton for the exact API contract.
