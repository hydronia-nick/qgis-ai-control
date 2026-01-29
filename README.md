# QGIS AI Tools

AI-powered control for QGIS via Model Context Protocol (MCP).

## What This Is

This project enables AI assistants (Claude Code, Cline, etc.) to autonomously control QGIS through a unified MCP interface.

**Features:**
- 🚀 Launch/kill QGIS processes
- 🎯 Full UI control (find widgets, click, interact)
- 🔄 Autonomous error recovery
- 📝 Complete audit trail
- 🛠️ 22 commands for comprehensive control

## Quick Start

### Installation

#### From GitHub

```bash
# Clone repository
git clone https://github.com/hydronia-nick/qgis-ai-control.git
cd qgis-ai-control

# Install Python dependencies
pip install requests psutil mcp

# Copy QGIS plugin to plugins folder
# Windows:
xcopy qgis-plugin\qgis_ai_bridge "C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins\qgis_ai_bridge" /E /I

# Mac:
cp -r qgis-plugin/qgis_ai_bridge ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux:
cp -r qgis-plugin/qgis_ai_bridge ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

# Configure MCP
# Edit ~/.claude/mcp.json (see INSTALLATION.md for details)
```

#### Manual Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed step-by-step instructions.

### Usage

**Check if QGIS running:**
```python
qgis_control({"command": "qgis.find_process"})
```

**Launch QGIS:**
```python
qgis_control({"command": "qgis.launch"})
```

**List all commands:**
```python
qgis_control({"command": "help"})
```

**See what happened:**
```python
qgis_control({"command": "qgis.read_log", "params": {"limit": 10}})
```

## Repository Structure

```
qgis-ai-control/                    (This repository)
├── README.md                       Quick start guide
├── INSTALLATION.md                 Detailed installation
├── .gitignore                      Git ignore rules
├── qgis-ai-development.code-workspace  VS Code workspace
├── mcp-server/                     MCP server (standalone)
│   ├── server.py                   Main MCP server
│   └── qgis_mcp_skills.md          Command reference
├── qgis-plugin/                    QGIS plugin files
│   └── qgis_ai_bridge/             Copy to QGIS plugins folder
│       ├── commands/               Command handlers
│       ├── COMMAND_REGISTRY.py     Command routing
│       └── api_server.py           HTTP server
└── docs/                           Documentation
    ├── IMPLEMENTATION_GUIDE.md     Full architecture
    └── VSCODE_SETUP.md             VS Code setup
```

**How it works:**
1. AI calls MCP tool: `qgis_control({"command": "..."})`
2. MCP server routes:
   - OS commands (launch, find_process) → Execute directly
   - API commands (widget.*, etc.) → Forward to QGIS HTTP API
3. QGIS plugin receives request, executes, returns result
4. AI receives structured response

## Folder Structure

```
qgis-ai-tools/
├── README.md                       (This file)
├── mcp-server/
│   ├── server.py                   Main MCP server
│   └── qgis_mcp_skills.md          Quick command reference
└── docs/
    ├── IMPLEMENTATION_GUIDE.md     Complete architecture & patterns
    └── VSCODE_SETUP.md             VS Code/Cline configuration
```

## Documentation

- **Quick Start:** `mcp-server/qgis_mcp_skills.md` (< 200 tokens)
- **Full Guide:** `docs/IMPLEMENTATION_GUIDE.md` (architecture, patterns, all commands)
- **VS Code Setup:** `docs/VSCODE_SETUP.md` (Cline configuration)

## Commands (22 total)

### OS-Level (work without QGIS running)
- `qgis.launch` - Launch QGIS executable
- `qgis.find_process` - Check if QGIS running
- `qgis.kill_process` - Kill QGIS processes

### QGIS Control (require QGIS running)
- **Lifecycle:** status, log, read_log, reload_plugin, restart, api_status, restart_api, execute_action
- **Widget Control:** list_windows, find, inspect, click, wait_for, set_text, select_item, send_keys
- **Recovery:** crash.save, crash.restore, crash.list
- **Error Handling:** error.detect, dialog.close

Full command reference: `qgis_control({"command": "help"})`

## Requirements

- Python 3.7+ with packages: `requests`, `psutil`, `mcp`
- QGIS 3.x installed
- Claude Code CLI or VS Code with Cline extension

## Development

This folder is meant to be portable. You can:
- Clone to any location
- Update MCP config to point to new location
- Everything works the same

The QGIS plugin (`qgis_ai_bridge/`) must stay in QGIS plugins folder.

## Configuration

**MCP Config:** `C:\Users\PC\.claude\mcp.json`
```json
{
  "mcpServers": {
    "qgis-control": {
      "command": "python",
      "args": [
        "C:\\Users\\PC\\Documents\\qgis-ai-tools\\mcp-server\\server.py"
      ]
    }
  }
}
```

## License

Custom development for QGIS AI automation.

## Status

✅ **Phase 1 & 2 Complete** - Full autonomous operation with form interaction
- 22 commands working
- Complete lifecycle control
- Error detection and recovery
- Form interaction (text input, dropdowns, keyboard)
- All operations via MCP

**Ready for production use!**
