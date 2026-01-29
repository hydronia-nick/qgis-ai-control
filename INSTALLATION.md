# QGIS AI Bridge - Installation Guide

Complete installation guide for setting up QGIS AI control on any system.

## Prerequisites

- ✅ Python 3.7 or higher
- ✅ QGIS 3.x installed
- ✅ Claude Code CLI or VS Code with Cline extension

## Important: Repository Structure

**This repository IS the QGIS plugin itself.** You clone it directly into your QGIS plugins folder, not to a separate location.

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install requests psutil mcp
```

### 2. Clone Repository Directly to QGIS Plugins Folder

**Windows:**
```bash
cd "C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins"
git clone https://github.com/hydronia-nick/qgis-ai-control.git qgis_ai_bridge
```

**Mac:**
```bash
cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/hydronia-nick/qgis-ai-control.git qgis_ai_bridge
```

**Linux:**
```bash
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/hydronia-nick/qgis-ai-control.git qgis_ai_bridge
```

**Note:** The repository clones directly as the plugin. No copying needed!

### 3. Configure MCP

**Create or edit:** `~/.claude/mcp.json`

**Windows:** `C:\Users\<YourUsername>\.claude\mcp.json`
**Mac/Linux:** `~/.claude/mcp.json`

**Windows Example:**
```json
{
  "mcpServers": {
    "qgis-control": {
      "command": "python",
      "args": [
        "C:\\Program Files\\QGIS 3.40.7\\apps\\qgis-ltr\\python\\plugins\\qgis_ai_bridge\\mcp-server\\server.py"
      ]
    }
  }
}
```

**Mac Example:**
```json
{
  "mcpServers": {
    "qgis-control": {
      "command": "python",
      "args": [
        "/Users/YOUR_USERNAME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis_ai_bridge/mcp-server/server.py"
      ]
    }
  }
}
```

**Linux Example:**
```json
{
  "mcpServers": {
    "qgis-control": {
      "command": "python",
      "args": [
        "/home/YOUR_USERNAME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_ai_bridge/mcp-server/server.py"
      ]
    }
  }
}
```

**Important:**
- Use FULL absolute path to the MCP server inside the plugin folder
- On Windows, use double backslashes: `"C:\\Users\\..."`
- Or use forward slashes: `"C:/Users/..."`

### 4. Enable QGIS Plugin

1. Launch QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Click **Installed**
4. Find **QGIS AI Bridge** and check the box to enable it
5. Verify in **Log Messages** panel → should see "QGIS AI Bridge: API server started on port 5557"

### 5. Restart Claude Code / Cline

**Claude Code CLI:**
```bash
# Just restart the terminal or run:
exit
# Then start Claude Code again
```

**VS Code (Cline):**
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type: "Cline: Restart MCP Servers"
3. Or restart VS Code

### 6. Verify Installation

Test in Claude Code or Cline:

```
Can you check if QGIS is running?
```

Should use:
```python
qgis_control({"command": "qgis.find_process"})
```

If not running, launch it:
```
Please launch QGIS
```

Should use:
```python
qgis_control({"command": "qgis.launch"})
```

Then verify API:
```
Check QGIS status
```

Should use:
```python
qgis_control({"command": "qgis.status"})
```

## VS Code Development Setup

**Option 1: Open workspace file**
```
File → Open Workspace from File
Select: qgis_ai_bridge/qgis-ai-bridge.code-workspace
```

**Option 2: Open folder directly**
```
File → Open Folder
Select: C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins\qgis_ai_bridge\
```

The repository IS the plugin, so you only need to open one folder.

## Troubleshooting

### MCP Tool Not Appearing

**Check 1: Config file location**
```bash
# Should exist:
~/.claude/mcp.json
```

**Check 2: Python can run server**
```bash
# Windows example:
python "C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins\qgis_ai_bridge\mcp-server\server.py"
# Should not error (will wait for input - Ctrl+C to exit)
```

**Check 3: Restart completely**
- Close Claude Code / VS Code completely
- Reopen

### QGIS Plugin Not Loading

**Check 1: Plugin in correct folder**
```
Must be in: .../plugins/qgis_ai_bridge/
Not: .../plugins/qgis_ai_bridge/qgis_ai_bridge/
```

**Check 2: Check QGIS plugin manager**
- Plugins → Manage and Install Plugins
- Click "Installed"
- Look for "QGIS AI Bridge"
- Enable if disabled

**Check 3: Check for errors**
- View → Panels → Log Messages
- Look for errors in startup

### API Not Responding

**Check 1: QGIS running?**
```python
qgis_control({"command": "qgis.find_process"})
```

**Check 2: Plugin loaded?**
- QGIS Log Messages panel
- Should see: "QGIS AI Bridge: API server started on port 5557"

**Check 3: Restart API**
```python
qgis_control({"command": "qgis.restart_api"})
```

**Check 4: Restart QGIS**
```python
qgis_control({"command": "qgis.kill_process"})
qgis_control({"command": "qgis.launch"})
# Wait 5 seconds
qgis_control({"command": "qgis.status"})
```

## File Structure After Installation

```
QGIS Plugins/qgis_ai_bridge/         (This IS the repository)
├── .git/                            Git repository
├── README.md
├── INSTALLATION.md                  This file
├── IMPLEMENTATION_GUIDE.md          Architecture & patterns
├── VSCODE_SETUP.md                  VS Code setup
├── qgis-ai-bridge.code-workspace    VS Code workspace
│
├── mcp-server/                      MCP server (subdirectory)
│   ├── server.py                    Main server
│   └── qgis_mcp_skills.md           Command reference
│
├── commands/                        Command handlers
│   ├── qgis_commands.py
│   ├── widget_commands.py
│   └── crash_commands.py
├── utils/                           Helper utilities
│   ├── widget_finder.py
│   ├── log_buffer.py
│   └── coordinate_helper.py
│
├── __init__.py                      Plugin entry
├── ai_bridge.py                     Plugin loader
├── api_server.py                    HTTP API
├── COMMAND_REGISTRY.py              Command routing
├── COMMAND_TEMPLATE.py              Template for new commands
├── config.json                      Configuration
└── metadata.txt                     QGIS metadata
```

**Key Point:** The repository lives IN the QGIS plugins folder. Git tracks the actual working files directly.

## Next Steps

1. Read `VSCODE_SETUP.md` for VS Code/Cline setup
2. Read `mcp-server/qgis_mcp_skills.md` for quick command reference
3. Read `IMPLEMENTATION_GUIDE.md` for architecture details
4. Try example workflows in README.md

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review `IMPLEMENTATION_GUIDE.md`
3. Check QGIS Log Messages panel
4. Use `qgis.read_log` command to see what's happening
