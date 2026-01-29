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

**Note:** This repository IS the QGIS plugin itself. Clone directly to your QGIS plugins folder.

```bash
# Install Python dependencies
pip install requests psutil mcp

# Clone repository directly to QGIS plugins folder
# Windows:
cd "C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins"
git clone https://github.com/hydronia-nick/qgis-ai-control.git qgis_ai_bridge

# Mac:
cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/hydronia-nick/qgis-ai-control.git qgis_ai_bridge

# Linux:
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/hydronia-nick/qgis-ai-control.git qgis_ai_bridge

# Configure MCP (see INSTALLATION.md for details)
# Windows: Edit C:\Users\YOUR_USERNAME\.claude\mcp.json
# Mac/Linux: Edit ~/.claude/mcp.json
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

**Important:** This repository IS the QGIS plugin. It lives directly in your QGIS plugins folder.

```
qgis_ai_bridge/                     (This repository = QGIS plugin)
├── .git/                           Git repository
├── README.md                       This file
├── INSTALLATION.md                 Detailed installation guide
├── IMPLEMENTATION_GUIDE.md         Full architecture & patterns
├── VSCODE_SETUP.md                 VS Code/Cline setup
├── .gitignore                      Git ignore rules
│
├── mcp-server/                     MCP server (subdirectory)
│   ├── server.py                   Main MCP server
│   └── qgis_mcp_skills.md          Command reference
│
├── commands/                       Command handlers
│   ├── qgis_commands.py
│   ├── widget_commands.py
│   └── crash_commands.py
├── utils/                          Helper utilities
│   ├── widget_finder.py
│   ├── log_buffer.py
│   └── coordinate_helper.py
│
├── COMMAND_REGISTRY.py             Command routing (single source of truth)
├── api_server.py                   HTTP API server (localhost:5557)
├── ai_bridge.py                    Plugin entry point
├── config.json                     Configuration
└── metadata.txt                    QGIS plugin metadata
```

**How it works:**
1. AI calls MCP tool: `qgis_control({"command": "..."})`
2. MCP server (mcp-server/server.py) routes:
   - OS commands (launch, find_process) → Execute directly
   - API commands (widget.*, etc.) → Forward to QGIS HTTP API
3. QGIS plugin (api_server.py) receives request, executes, returns result
4. AI receives structured response

## Documentation

- **Quick Start:** `mcp-server/qgis_mcp_skills.md` (< 200 tokens)
- **Full Guide:** `IMPLEMENTATION_GUIDE.md` (architecture, patterns, all commands)
- **VS Code Setup:** `VSCODE_SETUP.md` (Cline configuration)

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

**Git repository location:** This repository must stay in your QGIS plugins folder since it IS the plugin itself. All development happens directly in the QGIS plugins directory.

**Working with Git:**
- Changes are tracked immediately (no copying needed)
- Edit files directly in the plugins folder
- Commit and push as normal
- QGIS plugin reload picks up changes instantly

**VS Code Workspace:** See VSCODE_SETUP.md for multi-folder workspace configuration.

## Configuration

**MCP Config:** Update your `~/.claude/mcp.json` (or `C:\Users\YOUR_USERNAME\.claude\mcp.json` on Windows)

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

**Important:** Update the path to match your QGIS installation location and operating system.

## License

Custom development for QGIS AI automation.

## Status

✅ **Phase 1 & 2 Complete** - Full autonomous operation with form interaction
- 22 commands working
- Complete lifecycle control (launch, kill, restart QGIS)
- Error detection and recovery
- Form interaction (text input, dropdowns, keyboard)
- All operations via MCP

**Ready for production use!**

## Roadmap

**Phase 3: Essential GIS Operations** (13-15 commands)
- Layer management (add, remove, list, visibility, reorder)
- Project operations (open, save, get_info, set_crs)
- Map canvas control (zoom, pan, extent, refresh)

**Phase 4: Data Processing** (7-8 commands)
- Processing algorithms (list, run, get_result)
- Feature/attribute operations (select, query, get_selected)

**Phase 5: Output/Export** (3 commands)
- Export layer to file formats
- Export map as image/PDF

**Target:** 54-58 commands total for comprehensive GIS automation

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for detailed roadmap and implementation plans.
