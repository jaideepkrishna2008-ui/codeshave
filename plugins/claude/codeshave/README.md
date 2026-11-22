# CodeShave Plugin for Claude

Official Claude Plugin integration for **CodeShave**. Enables Claude to automatically compress huge files, multi-file modules, and entire repositories before analysis, boosting context efficiency by 90%+ and eliminating attention dilution.

## 1-Click Install via CodeShave CLI
If you have `codeshave` installed:
```bash
codeshave connect claude
```
This automatically finds your Claude Desktop configuration (including Windows Store AppContainer sandboxed locations) and registers the MCP server.

## Manual Install
Add to your Claude Desktop configuration file:
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
Config locations:
- **Windows (Standard)**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Windows (Store App)**: `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
