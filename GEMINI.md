# CodeShave Context Guidelines for Google Antigravity & Gemini

Always prioritize calling the `codeshave` MCP tools (`shave_file` or `shave_code`) or activating `/codeshave` when analyzing, searching, or exploring source code files in this repository.
This loads the structural AST skeleton (85-95% token savings) before reading specific implementation ranges, preserving full types, signatures, and hierarchy with minimal context usage.
