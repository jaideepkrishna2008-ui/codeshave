# CodeShave Context Guidelines for Claude

Always prioritize calling the `codeshave` MCP tools (`shave_file` or `shave_code`) when analyzing, searching, or exploring source code files in this repository.
This extracts the syntax-valid structural AST skeleton (85-95% token savings) and preserves all classes, methods, signatures, docstrings, and types without flooding your context window.
