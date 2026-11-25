# Privacy Policy — CodeShave

**Effective Date:** November 25, 2026  
**Publisher:** Jaideep Krishna A (`jaideepkrishna2008-ui`)

CodeShave is a 100% local, offline AST code compression tool and Model Context Protocol (MCP) server (`stdio` transport).

## Data Collection & Processing
- **No Telemetry or Analytics:** CodeShave collects zero usage metrics, analytics, crash reports, or tracking identifiers.
- **No Network Calls:** All AST parsing (`shave_code`, `shave_file`, `codeshave pack`, `codeshave diff`, `codeshave clip`) runs purely locally on your machine. No source code, file paths, or prompts are transmitted to external servers by CodeShave.
- **Local Filesystem Scope:** `shave_file` reads only the explicit local file path requested by your MCP client in read-only mode and never modifies or deletes files.

## Contact
For questions or security reports, open an issue at https://github.com/jaideepkrishna2008-ui/codeshave/issues or email `jaideepkrishna2008@gmail.com`.
