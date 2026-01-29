# VS Code Configuration for QGIS MCP Tool

This guide shows how to configure VS Code's Cline (Claude Code) extension to use the QGIS Control MCP tool.

## Prerequisites

1. ✅ VS Code installed
2. ✅ Cline extension installed (search "Cline" in VS Code extensions)
3. ✅ QGIS AI Bridge plugin installed and configured
4. ✅ Python with required packages (requests, psutil, mcp)

## Step 1: Locate Cline MCP Configuration

Cline uses the same MCP configuration as Claude Code CLI:

**Config file location:** `C:\Users\PC\.claude\mcp.json`

(This file is shared between Claude Code CLI and Cline extension)

## Step 2: Verify Configuration

Open `C:\Users\PC\.claude\mcp.json` and verify it contains:

```json
{
  "mcpServers": {
    "qgis-control": {
      "command": "python",
      "args": [
        "C:\\Program Files\\QGIS 3.40.7\\apps\\qgis-ltr\\python\\plugins\\qgis_mcp_server\\server.py"
      ]
    }
  }
}
```

**Important:** Use double backslashes (`\\`) in Windows paths!

## Step 3: Restart Cline

1. Open VS Code
2. Open Command Palette (Ctrl+Shift+P)
3. Type "Cline: Restart MCP Servers"
4. Or restart VS Code completely

## Step 4: Verify Tool is Available

Open Cline in VS Code and ask:
```
Can you use the qgis_control tool to check if QGIS is running?
```

Cline should use the tool:
```python
qgis_control({"command": "qgis.find_process"})
```

## Available Commands

See `qgis_mcp_skills.md` for full command reference. Key commands:

### Lifecycle (OS-level, work without QGIS running)
```python
qgis_control({"command": "qgis.find_process"})  # Check if running
qgis_control({"command": "qgis.launch"})  # Launch QGIS
qgis_control({"command": "qgis.kill_process"})  # Kill QGIS
```

### QGIS Control (require QGIS running)
```python
qgis_control({"command": "qgis.status"})  # Check QGIS version
qgis_control({"command": "widget.list_windows"})  # List dialogs
qgis_control({"command": "widget.find", "params": {"type": "title", "value": "Options"}})
qgis_control({"command": "qgis.execute_action", "params": {"action_name": "mActionShowPythonDialog"}})
qgis_control({"command": "qgis.read_log", "params": {"limit": 10}})  # See recent actions
```

## Troubleshooting

### Tool not appearing in Cline

1. Check config file exists: `C:\Users\PC\.claude\mcp.json`
2. Verify Python path is correct: `where python`
3. Check server.py exists at specified path
4. Restart VS Code completely
5. Check Cline logs: View → Output → Select "Cline" from dropdown

### "QGIS API not responding"

1. Check if QGIS is running:
   ```python
   qgis_control({"command": "qgis.find_process"})
   ```

2. If running but API not responding, restart:
   ```python
   qgis_control({"command": "qgis.kill_process"})
   qgis_control({"command": "qgis.launch"})
   ```

3. Wait 5 seconds for plugin to load, then:
   ```python
   qgis_control({"command": "qgis.status"})
   ```

### Python import errors

Install required packages:
```bash
pip install requests psutil mcp
```

## Usage Tips

1. **Always check if QGIS is running first:**
   ```python
   qgis_control({"command": "qgis.find_process"})
   ```

2. **Use help to see all commands:**
   ```python
   qgis_control({"command": "help"})
   ```

3. **Check logs to verify what happened:**
   ```python
   qgis_control({"command": "qgis.read_log", "params": {"limit": 5}})
   ```

4. **For diagnostics:**
   - All commands auto-log to QGIS message panel
   - Use `qgis.read_log` to see command history
   - Check QGIS "Log Messages" panel → "QGIS AI Bridge" category

## Example: Autonomous Workflow

```python
# 1. Check if QGIS running
result = qgis_control({"command": "qgis.find_process"})

# 2. Launch if not running
if not result["running"]:
    qgis_control({"command": "qgis.launch"})
    # Wait 5 seconds for startup

# 3. Verify API online
qgis_control({"command": "qgis.status"})

# 4. Open a dialog
qgis_control({"command": "qgis.execute_action",
              "params": {"action_name": "mActionOptions"}})

# 5. Find widgets
qgis_control({"command": "widget.find",
              "params": {"type": "class", "value": "QPushButton"}})

# 6. Close dialog
qgis_control({"command": "dialog.close",
              "params": {"objectName": "QgsOptionsBase"}})
```

## Files and Documentation

- **MCP Server:** `qgis_mcp_server/server.py`
- **QGIS Plugin:** `qgis_ai_bridge/`
- **Command Registry:** `qgis_ai_bridge/COMMAND_REGISTRY.py`
- **Skills Reference:** `qgis_mcp_server/qgis_mcp_skills.md`
- **Full Guide:** `qgis_ai_bridge/IMPLEMENTATION_GUIDE.md`

## Support

For issues or questions:
1. Check `IMPLEMENTATION_GUIDE.md` for architecture details
2. Review `qgis_mcp_skills.md` for command examples
3. Use `qgis.read_log` to see what's happening
4. Check QGIS Log Messages panel for errors
