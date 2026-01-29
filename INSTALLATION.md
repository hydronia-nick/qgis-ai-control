# QGIS AI Tools - Installation Guide

Complete installation guide for setting up QGIS AI control on any system.

## Prerequisites

- ✅ Python 3.7 or higher
- ✅ QGIS 3.x installed
- ✅ Claude Code CLI or VS Code with Cline extension

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install requests psutil mcp
```

### 2. Install QGIS Plugin

**Copy the plugin folder to QGIS plugins directory:**

**Windows:**
```
Copy qgis_ai_bridge/ to:
C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins\qgis_ai_bridge\
```

**Mac:**
```
Copy qgis_ai_bridge/ to:
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/qgis_ai_bridge/
```

**Linux:**
```
Copy qgis_ai_bridge/ to:
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_ai_bridge/
```

**Note:** The QGIS plugin MUST be in the plugins folder. Do not move it elsewhere.

### 3. Set Up MCP Server

**Option A: Use this portable folder (recommended)**

1. Copy this entire folder (`qgis-ai-tools/`) anywhere you want
2. Update MCP config (step 4) to point to new location

**Option B: Clone from repository**

If this is version-controlled:
```bash
git clone <repo-url> ~/Documents/qgis-ai-tools
cd ~/Documents/qgis-ai-tools
```

### 4. Configure MCP

**Create or edit:** `~/.claude/mcp.json`

**Windows:** `C:\Users\<YourUsername>\.claude\mcp.json`
**Mac/Linux:** `~/.claude/mcp.json`

```json
{
  "mcpServers": {
    "qgis-control": {
      "command": "python",
      "args": [
        "/FULL/PATH/TO/qgis-ai-tools/mcp-server/server.py"
      ]
    }
  }
}
```

**Important:**
- Use FULL absolute path
- On Windows, use double backslashes: `"C:\\Users\\..."`
- Or use forward slashes: `"C:/Users/..."`

### 5. Enable QGIS Plugin

1. Launch QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Click **Installed**
4. Find **QGIS AI Bridge** and check the box to enable it
5. Verify in **Log Messages** panel → should see "QGIS AI Bridge: API server started on port 5557"

### 6. Restart Claude Code / Cline

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

### 7. Verify Installation

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
Select: qgis-ai-tools/qgis-ai-development.code-workspace
```

**Option 2: Manually add folders**
1. Open VS Code
2. File → Add Folder to Workspace
3. Add: `qgis-ai-tools/`
4. Add: `C:\Program Files\QGIS 3.40.7\...\qgis_ai_bridge\`

## Troubleshooting

### MCP Tool Not Appearing

**Check 1: Config file location**
```bash
# Should exist:
~/.claude/mcp.json
```

**Check 2: Python can run server**
```bash
python /path/to/qgis-ai-tools/mcp-server/server.py
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
qgis-ai-tools/                       (Anywhere you want)
├── README.md
├── INSTALLATION.md                  (This file)
├── qgis-ai-development.code-workspace
├── mcp-server/
│   ├── server.py
│   └── qgis_mcp_skills.md
└── docs/
    ├── IMPLEMENTATION_GUIDE.md
    └── VSCODE_SETUP.md

QGIS Plugins/                        (Must be in QGIS folder)
└── qgis_ai_bridge/
    ├── __init__.py
    ├── api_server.py
    ├── COMMAND_REGISTRY.py
    ├── commands/
    │   ├── qgis_commands.py
    │   ├── widget_commands.py
    │   └── crash_commands.py
    └── utils.py
```

## Next Steps

1. Read `docs/VSCODE_SETUP.md` for VS Code/Cline setup
2. Read `mcp-server/qgis_mcp_skills.md` for quick command reference
3. Read `docs/IMPLEMENTATION_GUIDE.md` for architecture details
4. Try example workflows in README.md

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review `docs/IMPLEMENTATION_GUIDE.md`
3. Check QGIS Log Messages panel
4. Use `qgis.read_log` command to see what's happening
