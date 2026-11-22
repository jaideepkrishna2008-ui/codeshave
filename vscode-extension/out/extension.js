"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const child_process_1 = require("child_process");
const fs = require("fs");
const path = require("path");
function activate(context) {
    // Status Bar Item
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = "$(zap) CodeShave";
    statusBar.tooltip = "CodeShave: AST Code Context Compressor (90%+ Token Savings)";
    statusBar.command = "codeshave.compressFile";
    statusBar.show();
    context.subscriptions.push(statusBar);
    // Command: Compress Active File to Clipboard
    const compressFileCmd = vscode.commands.registerCommand("codeshave.compressFile", async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage("No active editor file to shave.");
            return;
        }
        const filePath = editor.document.uri.fsPath;
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "CodeShave: Compressing file...",
            cancellable: false,
        }, () => new Promise((resolve) => {
            (0, child_process_1.exec)(`codeshave clip "${filePath}"`, (error, stdout, stderr) => {
                if (error) {
                    // Fallback to uvx
                    (0, child_process_1.exec)(`uvx codeshave clip "${filePath}"`, (err2) => {
                        if (err2) {
                            vscode.window.showErrorMessage(`CodeShave error: ${err2.message}`);
                        }
                        else {
                            vscode.window.showInformationMessage("⚡ Shaved & copied to clipboard! (Ready to paste)");
                        }
                        resolve();
                    });
                }
                else {
                    vscode.window.showInformationMessage("⚡ Shaved & copied to clipboard! (Ready to paste)");
                    resolve();
                }
            });
        }));
    });
    context.subscriptions.push(compressFileCmd);
    // Command: Compress Selection to Clipboard
    const compressSelectionCmd = vscode.commands.registerCommand("codeshave.compressSelection", async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.selection.isEmpty) {
            vscode.window.showWarningMessage("Please select code to compress.");
            return;
        }
        const selectionText = editor.document.getText(editor.selection);
        // Simple structural trimmer
        const lines = selectionText.split("\n");
        const shaved = lines.filter((l) => l.trim().startsWith("def ") || l.trim().startsWith("class ") || l.trim().startsWith("function ") || l.trim().startsWith("interface ") || l.trim().startsWith("export "));
        const result = shaved.length > 0 ? shaved.join("\n") : selectionText;
        await vscode.env.clipboard.writeText(result);
        vscode.window.showInformationMessage("⚡ Shaved selection copied to OS clipboard!");
    });
    context.subscriptions.push(compressSelectionCmd);
    // Command: Auto-configure MCP in Workspace
    const connectMCPCmd = vscode.commands.registerCommand("codeshave.connectMCP", async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showWarningMessage("Open a workspace folder to configure MCP.");
            return;
        }
        const vscodeDir = path.join(workspaceFolders[0].uri.fsPath, ".vscode");
        const mcpPath = path.join(vscodeDir, "mcp.json");
        try {
            if (!fs.existsSync(vscodeDir)) {
                fs.mkdirSync(vscodeDir, { recursive: true });
            }
            let config = { mcpServers: {} };
            if (fs.existsSync(mcpPath)) {
                const raw = fs.readFileSync(mcpPath, "utf-8");
                config = JSON.parse(raw);
                if (!config.mcpServers) {
                    config.mcpServers = {};
                }
            }
            config.mcpServers["codeshave"] = {
                command: "uvx",
                args: ["codeshave", "mcp"],
            };
            fs.writeFileSync(mcpPath, JSON.stringify(config, null, 2) + "\n", "utf-8");
            vscode.window.showInformationMessage("✓ CodeShave MCP configured in .vscode/mcp.json!");
        }
        catch (err) {
            vscode.window.showErrorMessage(`Failed to configure MCP: ${err.message}`);
        }
    });
    context.subscriptions.push(connectMCPCmd);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map