# QGIS AI Bridge - Implementation Guide

**READ THIS FIRST - EVERY NEW CONVERSATION STARTS HERE**

**STATUS UPDATE 2026-01-29:** Phase 1 & 2 Complete, Phase 3 Started (23 commands)
- ✅ **Phase 1:** Full autonomous lifecycle (launch, kill, restart QGIS)
- ✅ **Phase 2:** Form interaction (set_text, select_item, send_keys)
- ✅ **Phase 3:** Layer operations started (layer.list complete)
- ✅ **UNIFIED MCP:** Single qgis-control server handles both OS-level and API commands
- ✅ Autonomous UI control (discover, interact, wait, detect errors, recover)
- 📋 **NEW PRIORITY:** Workflow recording system for OilFlow2D proof of concept
- 🎥 **Phase A (Next):** Build workflow.* commands (record, stop, add_note, list, get)
- 🎯 **Strategy:** OilFlow2D automation first (proof of concept), then generalize to full GIS
- 🚀 **Next:** workflow.record_start (capture user interactions for workflow documentation)

---

## 🎯 Core Principles

### 1. Unified MCP Architecture (MANDATORY)

**One MCP server, two command types:**

```
┌────────────────────────────────────────────┐
│  MCP Server (qgis_mcp_server/server.py)    │  ← UNIFIED SERVER
│  ├─ OS Commands (launch, find_process)     │  ← Execute directly
│  │  • Work without QGIS running            │
│  │  • psutil, subprocess                   │
│  └─ API Commands (status, widget.*, etc)   │  ← Forward to QGIS
│     • Require QGIS running                 │
│     • HTTP localhost:5557                  │
└────────────────┬───────────────────────────┘
                 │ HTTP (localhost:5557)
┌────────────────▼───────────────────────────┐
│  QGIS Plugin (qgis_ai_bridge/)             │  ← YOU BUILD THIS
│  - Command router /api/command             │
│  - Handles 19 commands in registry         │
│  - Controls QGIS directly via Qt/PyQGIS    │
└────────────────────────────────────────────┘
```

**Rule: All commands via single qgis_control MCP tool, no exceptions**

### 2. Command Pattern

**One command router handles everything. All commands follow the same pattern. No exceptions.**

```json
qgis_control({
  "command": "category.action",
  "params": {/* command-specific */}
})
```

**This pattern is enforced by code structure, not documentation.**

### 3. Automatic Audit Trail

**Every MCP command automatically logs to QGIS message panel:**
- ✓ Success: `✓ command.name | params: {...}`
- ✗ Failure: `✗ command.name failed: error message`
- ❌ Invalid: `❌ Invalid command: command.name`

**AI agents can read the log programmatically:**
```python
qgis_control({"command": "qgis.read_log", "params": {"limit": 20}})
# Returns last 20 messages with timestamps and levels
```

**Check Log Messages Panel (View → Panels → Log Messages) → "QGIS AI Bridge" for full history.**

**Implementation:**
- Log buffer stores last 100 messages in memory (circular buffer)
- Both `qgis.log` command and automatic audit trail write to buffer
- Commands `qgis.log` and `qgis.read_log` skip auto-logging to avoid recursion/spam

### 4. Self-Management (Autonomous Operation)

**The plugin can manage itself via MCP commands:**

**Reload itself after code changes:**
```python
qgis_control({"command": "qgis.reload_plugin"})
# Uses QTimer with 1-second delay to send response first, then reload
# Prevents crashes from reloading during request handling
```

**Check API server status:**
```python
qgis_control({"command": "qgis.api_status"})
# Returns: {"api_running": true, "port": 5557, "host": "127.0.0.1"}
```

**Restart API server (kills zombie processes):**
```python
qgis_control({"command": "qgis.restart_api"})
# Stops server, kills any zombie processes on port, restarts
# Fixes port conflicts from crashed instances
```

**Restart entire QGIS:**
```python
qgis_control({"command": "qgis.restart", "params": {"save_project": true}})
# Saves project, launches new QGIS, exits current (1-second delay)
```

**Why this matters:**
- AI agent can recover from errors autonomously
- No human intervention needed for common issues
- Enables true hands-free operation

---

## 📋 Quick Start (New Conversation Checklist)

1. ✅ Read this file
2. ✅ Check `COMMAND_REGISTRY.py` for existing commands
3. ✅ Test that QGIS is running: `curl http://localhost:5557/api/command -d '{"command":"qgis.status"}'`
4. ✅ See what works: Check "Current Status" section below
5. ✅ Continue from "Next Command to Build"
6. ✅ Follow "Adding a Command" workflow EXACTLY

**Never skip steps. Never deviate from pattern.**

---

## 🏗️ Architecture (Token-Efficient)

### The ONLY Way Commands Work

```
MCP Client                    Plugin                     QGIS
    │                            │                         │
    ├─ {command: "dialog.open"} ─┤                         │
    │                            ├─ Route to handler       │
    │                            ├─ Validate params        │
    │                            ├─ Execute ──────────────►│
    │                            │                         │
    │◄─── {success: true} ───────┤                         │
```

### Why This Pattern

**Bad (50 tools × 150 tokens = 7,500 tokens):**
- `qgis_open_dialog(...)`
- `qgis_close_dialog(...)`
- `qgis_set_field(...)`
- ... 47 more tools

**Good (1 tool × 60 tokens = 60 tokens):**
- `qgis_control({command: "dialog.open", ...})`
- `qgis_control({command: "dialog.close", ...})`
- `qgis_control({command: "form.set_field", ...})`

**Result: 99% token reduction, infinite scalability**

---

## 🎥 Workflow Recording & Documentation (CRITICAL)

### The Problem

Without workflow documentation, AI must:
- ❌ Guess action names for plugin menus
- ❌ Discover dialog objectNames through trial-error
- ❌ Figure out sequence every conversation
- ❌ Waste 2000+ tokens on discovery

**This is unsustainable for production workflows.**

### The Solution: Workflow Library

Create **token-efficient workflow documentation** for common patterns:
- OilFlow2D project creation
- OilFlow2D simulation runs
- General QGIS data loading workflows
- Standard GIS operations

**Format:** Similar to `qgis_mcp_skills.md` but for **step-by-step workflows**

### Workflow Recording Commands

**workflow.record_start** - Begin capturing user interactions
```python
qgis_control({
    "command": "workflow.record_start",
    "params": {"workflow_name": "oilflow2d_new_project"}
})
```
- Starts Qt event capture
- Filters to significant events: clicks, text input, dialogs, dropdowns
- Auto-logs widget properties (objectName, class, text, window title)
- Timestamps all events

**workflow.record_stop** - End recording and generate workflow
```python
qgis_control({"command": "workflow.record_stop"})
```
- Stops event capture
- Generates structured markdown workflow document
- Saves to `mcp-server/workflows/<name>.md`
- Returns summary with command count

**workflow.add_note** - Add manual annotation during recording
```python
qgis_control({
    "command": "workflow.add_note",
    "params": {"note": "This sets the output coordinate system"}
})
```
- Adds context that events alone can't capture
- User can explain WHY a step matters

**workflow.list** - List all saved workflows
```python
qgis_control({"command": "workflow.list"})
```

**workflow.get** - Retrieve specific workflow
```python
qgis_control({
    "command": "workflow.get",
    "params": {"workflow_name": "oilflow2d_new_project"}
})
```

### Workflow Document Standard

**Location:** `mcp-server/workflows/<workflow_name>.md`

**Format:**
```markdown
# Workflow: OilFlow2D New Project

**Purpose:** Create new OilFlow2D model project
**Prerequisites:** QGIS running, OilFlow2D plugin enabled
**Estimated time:** 15 seconds
**Recorded:** 2026-01-29

## Steps

### 1. Open New Project Dialog
- **Command:** qgis.execute_action
- **Params:** {"action_name": "oilflow_new_project"}
- **Wait:** 0.5s
- **Expected:** Dialog "New OilFlow2D Project" appears
- **Note:** This is the OilFlow2D menu → New Project action

### 2. Set Project Name
- **Command:** widget.set_text
- **Target:** objectName="lineEdit_projectName"
- **Value:** <user_provided>
- **Wait:** 0.1s
- **Note:** Project name will be used for output files

### 3. Select CRS
- **Command:** widget.select_item
- **Target:** objectName="comboBox_crs"
- **Value:** "EPSG:26918" (or <user_provided>)
- **Wait:** 0.1s

### 4. Click Create
- **Command:** widget.click
- **Target:** objectName="buttonBox" → button with text="OK"
- **Wait:** 1.0s
- **Verify:** widget.wait_for objectName="OilFlow2DProject" state="visible"

## Troubleshooting
- If action not found → plugin not enabled (use plugin.list)
- If dialog doesn't appear → check qgis.read_log
- If button not found → inspect with widget.list_windows

## Variables
- `<user_provided>` = Values user must specify each time
- Can be parameterized in automation scripts
```

**Token Budget:** ~250-300 tokens per workflow (vs 2000+ for discovery)

### Workflow Library Structure

```
mcp-server/
├── server.py
├── qgis_mcp_skills.md           ← Command reference (<200 tokens)
└── workflows/                    ← NEW: Workflow library
    ├── README.md                ← Index of workflows with descriptions
    ├── oilflow2d_new_project.md
    ├── oilflow2d_add_boundary.md
    ├── oilflow2d_configure_simulation.md
    ├── oilflow2d_run_simulation.md
    ├── oilflow2d_export_results.md
    └── general_qgis_load_shapefile.md
```

### Standards for Recording

**DO:**
- ✅ Record complete workflows end-to-end
- ✅ Add notes explaining WHY steps matter
- ✅ Include verification steps (widget.wait_for)
- ✅ Document expected dialogs/windows
- ✅ Note any prerequisites
- ✅ Include troubleshooting section
- ✅ Mark variable values as `<user_provided>`
- ✅ Keep workflows focused (one task per workflow)

**DON'T:**
- ❌ Record exploratory clicking (clean before saving)
- ❌ Skip wait times (causes race conditions)
- ❌ Hardcode paths (use variables)
- ❌ Assume widgets are visible (add wait_for)
- ❌ Skip error handling steps

### Recording Process

1. **Plan:** Decide what workflow to record
2. **Start:** Call workflow.record_start
3. **Execute:** Perform the workflow in QGIS as user
4. **Annotate:** Add notes for important steps
5. **Stop:** Call workflow.record_stop
6. **Review:** Check generated markdown
7. **Edit:** Clean up, add troubleshooting
8. **Test:** Have AI follow workflow autonomously
9. **Commit:** Save to git

### Priority: Proof of Concept First

**Phase A: Build Recording System (4-5 commands)**
- ⬜ workflow.record_start
- ⬜ workflow.record_stop
- ⬜ workflow.add_note
- ⬜ workflow.list
- ⬜ workflow.get

**Phase B: Record OilFlow2D Workflows**
- 🎥 Record: "Create New OilFlow2D Project"
- 🎥 Record: "Add Boundary Shapefile"
- 🎥 Record: "Configure Simulation Parameters"
- 🎥 Record: "Run Simulation"
- 🎥 Record: "Export Results"

**Phase C: Implement Missing Commands (as discovered)**
- Implement only what workflows reveal we need
- Priority based on actual usage, not theory

**Phase D: Test Full Automation**
- AI follows workflows autonomously
- Verify end-to-end automation works
- Document any gaps

**Phase E: Generalize**
- Continue with Phase 3-5 GIS commands
- Build general workflow library

### Why This Matters

**Token Efficiency:**
- Command reference: ~200 tokens (qgis_mcp_skills.md)
- Workflow library: ~250 tokens per workflow
- Total: ~1500 tokens for 5 OilFlow2D workflows
- **vs 10,000+ tokens for discovery each conversation**

**Reusability:**
- Once recorded, works forever
- Any AI can follow workflows
- No re-learning or re-discovering

**Production Ready:**
- Real workflows, not theoretical commands
- Tested patterns that actually work
- Documentation that survives conversations

**Prioritization:**
- Build only what you actually use
- Proof of concept before generalization
- OilFlow2D automation first, GIS commands second

---

## 📁 File Structure (Self-Enforcing)

```
qgis_ai_bridge/
├── IMPLEMENTATION_GUIDE.md       ← YOU ARE HERE (read first, always)
├── COMMAND_REGISTRY.py           ← Lists ALL commands (single source of truth)
├── COMMAND_TEMPLATE.py           ← Copy this for new commands
│
├── api_server.py                 ← Has ONE route: /api/command
├── ai_bridge.py                  ← Plugin entry point
├── config.json                   ← Port: 5557
│
├── commands/                     ← ALL command handlers live here
│   ├── __init__.py              ← Imports all handlers
│   ├── qgis_commands.py         ← qgis.* (status, log, crash)
│   ├── dialog_commands.py       ← dialog.* (open, close, list)
│   ├── form_commands.py         ← form.* (fill, submit, validate)
│   └── [new_category]_commands.py
│
└── utils/
    ├── widget_finder.py
    └── state_manager.py
```

**Rule: If you need to create a file not in this structure, you're doing it wrong.**

---

## ⚙️ How It Works (Code Structure)

### 1. Single Command Router (api_server.py)

```python
@app.route('/api/command', methods=['POST'])
def execute_command():
    """ONLY endpoint - routes all commands and logs audit trail"""
    data = request.get_json()
    command = data.get('command')
    params = data.get('params', {})

    # Special: help
    if command == 'help':
        return jsonify(COMMAND_REGISTRY.get_help())

    # Validate
    is_valid, error = COMMAND_REGISTRY.validate_command(command)
    if not is_valid:
        # Log invalid command
        QgsMessageLog.logMessage(f"❌ Invalid: {command}", 'QGIS AI Bridge', Qgis.Warning)
        return jsonify({"success": False, "error": error}), 404

    # Execute
    handler = COMMAND_REGISTRY.get(command)
    result = handler(params)

    # Automatic audit trail logging (skip qgis.log to avoid recursion)
    if command != 'qgis.log':
        if result.get('success'):
            QgsMessageLog.logMessage(f"✓ {command} | {params}", 'QGIS AI Bridge', Qgis.Info)
        else:
            QgsMessageLog.logMessage(f"✗ {command} failed: {result.get('error')}", 'QGIS AI Bridge', Qgis.Warning)

    return jsonify(result)
```

**Audit Trail:** Every command automatically logs to QGIS message panel with ✓ (success) or ✗ (failure).

### 2. Command Registry (COMMAND_REGISTRY.py)

```python
"""
COMMAND REGISTRY - Single source of truth for all commands

To add a command:
1. Import the handler
2. Add to COMMANDS dict
3. Add description to HELP
4. Test it
"""

from commands.qgis_commands import qgis_status, qgis_log
from commands.dialog_commands import dialog_open, dialog_close

COMMANDS = {
    # Format: "category.action": handler_function
    "qgis.status": qgis_status,
    "qgis.log": qgis_log,
    "dialog.open": dialog_open,
    "dialog.close": dialog_close,
    # Add new commands here
}

HELP = {
    "qgis.status": {
        "params": {},
        "returns": {"running": bool, "version": str},
        "example": {"command": "qgis.status"}
    },
    "qgis.log": {
        "params": {"message": str, "level": str},
        "returns": {"success": bool},
        "example": {"command": "qgis.log", "params": {"message": "Test", "level": "info"}}
    },
    # Add new help entries here
}

def get(command):
    """Get handler for command"""
    return COMMANDS.get(command)

def list_commands():
    """List all available commands"""
    return list(COMMANDS.keys())

def get_help(command=None):
    """Get help for one or all commands"""
    if command:
        return HELP.get(command, {"error": "Command not found"})
    return {"commands": HELP}
```

### 3. Command Handler Template (COMMAND_TEMPLATE.py)

```python
"""
Template for new commands - COPY THIS FILE

1. Copy this file to commands/[category]_commands.py
2. Rename function to match command (e.g., dialog_open)
3. Update params and logic
4. Add to COMMAND_REGISTRY.py
5. Test with curl
"""

def command_template(params):
    """
    Brief description of what this command does

    Args:
        params (dict): Command parameters
            - required_param (str): Description
            - optional_param (str, optional): Description

    Returns:
        dict: {"success": bool, "result": any, "error": str}
    """
    # 1. Validate params
    if 'required_param' not in params:
        return {
            "success": False,
            "error": "Missing required_param"
        }

    # 2. Do the work (keep logic simple here, use utils for complex stuff)
    try:
        result = _do_work_internal(params['required_param'])
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _do_work_internal(param):
    """Complex logic goes in internal functions"""
    # All PyQt5, widget finding, etc. goes here
    # Keep the main handler clean and simple
    pass
```

---

## 🔧 Adding a Command (Mandatory Workflow)

**CRITICAL: EVERY command requires implementation on BOTH sides**

```
┌─────────────────────────┐
│   MCP Server Side       │  You implement this
│   (qgis_mcp_server/)    │
└───────────┬─────────────┘
            │ HTTP
┌───────────▼─────────────┐
│   QGIS Plugin Side      │  You implement this
│   (qgis_ai_bridge/)     │
└─────────────────────────┘
```

**Rule: No curl testing. Only MCP tool testing.**

### Step 1: Define Command

**Write this down before coding:**
```
Command: dialog.open
Category: dialog
Action: open
Purpose: Opens a plugin dialog
Params: {"plugin": str, "dialog": str}
Returns: {"success": bool, "dialog_id": str}
```

### Step 2: Create Handler

1. Copy `COMMAND_TEMPLATE.py` to `commands/dialog_commands.py` (if new category)
2. Rename function: `dialog_open`
3. Implement logic:

```python
def dialog_open(params):
    """Opens a plugin dialog"""
    if 'plugin' not in params or 'dialog' not in params:
        return {"success": False, "error": "Missing plugin or dialog"}

    try:
        return _open_dialog_internal(params['plugin'], params['dialog'])
    except Exception as e:
        return {"success": False, "error": str(e)}

def _open_dialog_internal(plugin, dialog):
    from qgis.utils import plugins

    if plugin not in plugins:
        return {"success": False, "error": f"Plugin {plugin} not loaded"}

    action = getattr(plugins[plugin], dialog, None)
    if not action:
        return {"success": False, "error": f"Dialog {dialog} not found"}

    action.trigger()
    return {"success": True, "dialog_id": f"{plugin}_{dialog}"}
```

### Step 3: Register Command

Edit `COMMAND_REGISTRY.py`:

```python
# Add import
from commands.dialog_commands import dialog_open

# Add to COMMANDS
COMMANDS = {
    # ...existing...
    "dialog.open": dialog_open,
}

# Add to HELP
HELP = {
    # ...existing...
    "dialog.open": {
        "params": {"plugin": str, "dialog": str},
        "returns": {"success": bool, "dialog_id": str},
        "example": {"command": "dialog.open", "params": {"plugin": "OilFlow2DMS", "dialog": "newproject"}}
    },
}
```

### Step 4: Test ONLY via MCP (MANDATORY)

**❌ WRONG - Do NOT test with curl:**
```bash
curl -X POST http://localhost:5557/api/command ...  # NEVER DO THIS
```

**✅ CORRECT - Test via MCP tool:**
```python
# Use MCP tool directly (if available in your environment)
qgis_control({
    "command": "dialog.open",
    "params": {"plugin": "OilFlow2DMS", "dialog": "newproject"}
})
```

**Or test MCP server directly:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"qgis_control","arguments":{"command":"dialog.open","params":{"plugin":"OilFlow2DMS","dialog":"newproject"}}}}' | python "C:\Program Files\QGIS 3.40.7\apps\qgis-ltr\python\plugins\qgis_mcp_server\server.py"
```

**Expected:** `{"content": [{"type": "text", "text": "{\"success\": true, ...}"}]}`

### Step 5: Verify Visually

**CRITICAL: API success ≠ actual success**

- Does the dialog actually appear on screen?
- Is it visible and in focus?
- Can you interact with it?

**If NO:** Document in "Known Limitations" section below

### Step 6: Update Documentation (MANDATORY)

**A. Update IMPLEMENTATION_GUIDE.md (this file):**
- Add ✅ to "Current Status" section with example
- Add ❌ to "Known Limitations" if fails
- Update "Next Command to Build"
- Update command count in footer

**B. Update qgis_mcp_skills.md (MCP server directory):**
- Add command to relevant category list
- Keep it BRIEF (just command name)
- This file MUST stay under 200 tokens
- This is what AI loads to learn the tool

**Example update to qgis_mcp_skills.md:**
```markdown
**dialog.*** - UI Control (list, open, close, find)
```

### Step 7: Commit

**Only commit if:**
- Command is in registry
- Command is tested
- Status is documented
- Visual verification done

---

## 📊 Current Status

### ✅ Working Commands

**qgis.status** - Check if QGIS is running
```python
qgis_control({"command": "qgis.status"})
# Returns: {"success": true, "running": true, "version": "3.40.7", "platform": "Windows"}
```

**qgis.log** - Log messages to QGIS message panel
```python
qgis_control({
    "command": "qgis.log",
    "params": {"message": "Test", "level": "info"}
})
# Returns: {"success": true, "level": "info"}
```

**qgis.read_log** - Read recent log messages from buffer
```python
qgis_control({
    "command": "qgis.read_log",
    "params": {"limit": 10}
})
# Returns: {"success": true, "messages": [...], "count": 10}
```

**qgis.reload_plugin** - Reload plugin via MCP (self-reload)
```python
qgis_control({
    "command": "qgis.reload_plugin",
    "params": {"plugin_name": "qgis_ai_bridge"}
})
# Returns: {"success": true, "reloading": true, "note": "Plugin will reload in 1 second"}
```

**qgis.restart** - Restart QGIS application
```python
qgis_control({
    "command": "qgis.restart",
    "params": {"save_project": true}
})
# Returns: {"success": true, "restarting": true, "saved": false}
```

**qgis.api_status** - Check API server status
```python
qgis_control({"command": "qgis.api_status"})
# Returns: {"success": true, "api_running": true, "port": 5557, "host": "127.0.0.1"}
```

**qgis.restart_api** - Restart API server and kill zombie processes
```python
qgis_control({"command": "qgis.restart_api"})
# Returns: {"success": true, "restarted": true, "port": 5557, "running": true}
```

**crash.save** - Save checkpoint before risky operations
```python
qgis_control({
    "command": "crash.save",
    "params": {"operation": "opening dialog"}
})
# Returns: {"success": true, "checkpoint_id": "checkpoint_20260129_120650", "project_path": "[Unsaved Project]"}
```

**crash.restore** - Restore from checkpoint
```python
qgis_control({
    "command": "crash.restore",
    "params": {"checkpoint_id": "checkpoint_20260129_120650"}
})
# Returns: {"success": true, "restored": true, "project_path": "[Unsaved Project]"}
```

**crash.list** - List all checkpoints
```python
qgis_control({"command": "crash.list"})
# Returns: {"success": true, "checkpoints": [...], "count": 1}
```

**widget.wait_for** - Wait for widget state changes
```python
qgis_control({
    "command": "widget.wait_for",
    "params": {"objectName": "dlg_project", "state": "visible", "timeout": 5}
})
# Returns: {"success": true, "condition_met": true, "elapsed_time": 0.018}
```

**error.detect** - Detect visible error dialogs
```python
qgis_control({"command": "error.detect"})
# Returns: {"success": true, "errors": [], "count": 0, "has_errors": false}
```

**dialog.close** - Close dialogs programmatically
```python
qgis_control({"command": "dialog.close", "params": {"title": "Error"}})
# Returns: {"success": true, "closed": true, "method": "reject()"}
```

**qgis.read_python_console** - Read Python console output
```python
qgis_control({
    "command": "qgis.read_python_console",
    "params": {"limit": 20, "filter": "error"}
})
# Returns: {"success": true, "output": "...", "lines": [...]}
```

**layer.list** - List all layers in current project
```python
qgis_control({
    "command": "layer.list",
    "params": {"include_metadata": True}
})
# Returns: {"success": true, "layers": [...], "count": 0}
# Each layer includes: id, name, type, is_valid, is_visible, crs, extent, feature_count, source, provider
```

### 🔧 In Progress

**Phase A.2: Record OilFlow2D Workflows (NEXT)**
- ⬜ oilflow2d_new_project.md - Record actual OilFlow2D project creation
- ⬜ oilflow2d_add_boundary.md
- ⬜ oilflow2d_configure_simulation.md
- ⬜ oilflow2d_run_simulation.md
- ⬜ oilflow2d_export_results.md

**Phase A.1: Workflow Recording System ✅ COMPLETE (2026-01-29)**
- ✅ workflow.record_start - Begin capturing interactions
- ✅ workflow.record_stop - Generate workflow document
- ✅ workflow.add_note - Manual annotations
- ✅ workflow.list - List saved workflows
- ✅ workflow.get - Retrieve specific workflow

**Phase 3: Essential GIS Operations**
- ✅ layer.list - List all layers with metadata (COMPLETE - 2026-01-29)
- ⬜ layer.add - Paused pending workflow discovery

### ⬜ Planned (NEW Priority Order)

**Phase A: Workflow Recording & OilFlow2D Proof of Concept**

**Step 1: Build Recording System (4-5 commands) - PRIORITY #1**
1. workflow.record_start - Begin Qt event capture
2. workflow.record_stop - Generate structured markdown
3. workflow.add_note - Add manual annotations during recording
4. workflow.list - List all saved workflows
5. workflow.get - Retrieve specific workflow for AI to follow

**Step 2: Record OilFlow2D Workflows**
- 🎥 Workflow: "OilFlow2D New Project"
- 🎥 Workflow: "OilFlow2D Add Boundary Data"
- 🎥 Workflow: "OilFlow2D Configure Simulation"
- 🎥 Workflow: "OilFlow2D Run Simulation"
- 🎥 Workflow: "OilFlow2D Export Results"

**Step 3: Implement Commands Discovered During Recording**
- Implement ONLY commands that workflows reveal are needed
- Priority based on actual usage frequency in workflows
- Examples: layer.add, project.save, plugin.list (as discovered)

**Step 4: Test Full Autonomous OilFlow2D Workflow**
- AI follows recorded workflows end-to-end
- No manual intervention
- Document any gaps or failures
- Iterate until fully autonomous

**Phase B: Complete OilFlow2D Critical Commands (as discovered)**
- Commands will be prioritized based on workflow recordings
- Estimated: layer.add, project.save, project.new, plugin.list

**Phase C: Generalize to Standard GIS Operations (Phase 3-5 from original plan)**

**Layer Management (remaining 5-6 commands):**
1. ✅ layer.list - Get all layers with properties - **DONE**
2. layer.add - Add vector/raster layer to project (may be done in Phase B)
3. layer.remove - Remove layer from project
4. layer.set_active - Set the active layer
5. layer.set_visible - Show/hide layer
6. layer.reorder - Change layer order in TOC
7. layer.get_info - Get detailed layer metadata

**Project Operations (3-4 commands):**
8. project.new - Create new project (may use qgis.execute_action)
9. project.open - Open existing project file
10. project.save - Save current project
11. project.save_as - Save project to new location
12. project.get_info - Get project properties (CRS, file path, layers, etc.)
13. project.set_crs - Set project coordinate system

**Map Canvas Control (4-5 commands):**
14. canvas.zoom_full - Zoom to full extent
15. canvas.zoom_to_layer - Zoom to specific layer
16. canvas.zoom_to_extent - Zoom to coordinates (xmin, ymin, xmax, ymax)
17. canvas.pan - Pan to location (x, y)
18. canvas.refresh - Refresh map view
19. canvas.get_extent - Get current visible extent
20. canvas.set_crs - Set canvas CRS

**Phase 4: Data Processing (Target: 7-8 commands)**

**Processing Algorithms (3-4 commands):**
21. processing.list_algorithms - List available processing algorithms (with search/filter)
22. processing.get_params - Get algorithm parameters and types
23. processing.run - Execute processing algorithm with params
24. processing.get_result - Get processing results/output

**Feature/Attribute Operations (3-4 commands):**
25. features.select_by_expression - Select features using QGIS expression
26. features.get_selected - Get selected feature attributes and geometry
27. features.clear_selection - Clear feature selection
28. attribute_table.open - Open attribute table for layer
29. features.query - Query features by attributes (SQL-like)

**Phase 5: Output/Export (Target: 3 commands)**

**Data Export (3 commands):**
30. export.layer - Export layer to file (shapefile, geojson, gpkg, etc.)
31. export.map_image - Export map canvas as image (png, jpg, format, dpi)
32. export.pdf - Export map to PDF

**Future Phases (Lower Priority):**

**Styling/Symbology (3-4 commands):**
- style.apply - Apply style file (.qml) to layer
- style.set_renderer - Set renderer type (single, categorized, graduated)
- style.set_color_ramp - Apply color scheme
- style.get_current - Get current layer style

**Print Layouts (3 commands):**
- layout.list - List print layouts
- layout.create - Create new layout
- layout.export - Export layout to PDF/image

**Plugin Management (3 commands):**
- plugin.list - List installed plugins with status
- plugin.enable - Enable plugin
- plugin.disable - Disable plugin

**Target Command Counts:**
- Phase 3: 13-15 commands → **~35-37 total**
- Phase 4: 7-8 commands → **~42-45 total**
- Phase 5: 3 commands → **~45-48 total**
- Future: 9-10 commands → **~54-58 total**

---

## ❌ Known Limitations

### 1. Modal Dialogs Crash QGIS
**Command:** N/A (would be dangerous to implement)
**Problem:** `QMessageBox.information()` causes immediate crash
**Why:** Blocks main thread, kills Flask server
**Solution:** Use `qgis.log` instead
**Date Found:** 2026-01-29

### 2. Self-Modifying Commands Need Delays
**Commands:** qgis.reload_plugin, qgis.restart
**Problem:** Reloading/restarting during request handling causes crash
**Why:** Module cache cleared while code is still executing
**Solution:** Use QTimer.singleShot(1000, ...) to delay execution until after response sent
**Status:** ✅ FIXED with delayed execution
**Date Found:** 2026-01-29

### 3. Dialog Visibility Unconfirmed
**Command:** dialog.open (when implemented)
**Problem:** `trigger()` returns success but dialog may not appear
**Status:** NEEDS TESTING
**Next Step:** Build dialog.open and manually verify

### 4. API Restart Can Crash QGIS
**Command:** qgis.restart_api
**Problem:** Can cause QGIS to crash during API server restart
**Why:** Flask server restart while handling requests can destabilize QGIS
**Workaround:** Use qgis.kill_process + qgis.launch for full restart instead
**Status:** ⚠️ USE WITH CAUTION
**Date Found:** 2026-01-29

---

## 🧪 Testing Checklist

Before marking any command as ✅ Working:

- [ ] Command in COMMAND_REGISTRY.py
- [ ] Handler follows template pattern
- [ ] Curl test succeeds
- [ ] Visual verification done (if UI command)
- [ ] Error cases tested
- [ ] Help entry added
- [ ] This file updated

**Skip ANY step = command not complete**

---

## 🚀 Next Command to Build

**PRIORITY SHIFT: Workflow Recording System First**

**Command:** workflow.record_start
**Priority:** CRITICAL (Foundation for OilFlow2D automation)
**Purpose:** Begin recording user interactions to generate workflow documentation
**Params:** `{"workflow_name": str, "description": str (optional)}`
**Returns:** `{"success": bool, "recording": bool, "workflow_name": str, "start_time": str}`

**Why next:** We need workflow documentation BEFORE building more commands. Recording actual OilFlow2D workflows will:
1. Reveal exactly what commands we need (prioritize by actual usage)
2. Document exact action names, dialog objectNames, sequences
3. Create token-efficient workflow library (~250 tokens vs 2000+ for discovery)
4. Enable proof of concept for OilFlow2D automation
5. Validate our approach before building 30+ more commands

**Implementation approach for workflow.record_start:**
```python
from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QApplication
import datetime

class WorkflowRecorder(QObject):
    """Event filter to capture significant Qt events"""

    def __init__(self):
        super().__init__()
        self.recording = False
        self.events = []
        self.workflow_name = None
        self.start_time = None

    def eventFilter(self, obj, event):
        """Filter Qt events and log significant ones"""
        if not self.recording:
            return False

        # Capture significant events only
        if event.type() in [
            QEvent.MouseButtonPress,  # Clicks
            QEvent.KeyPress,          # Keyboard input
            QEvent.Show,              # Dialog opens
            QEvent.Hide,              # Dialog closes
            QEvent.FocusIn,           # Widget focus
        ]:
            self.log_event(obj, event)

        return False  # Don't block events

    def log_event(self, obj, event):
        """Log event with widget properties"""
        event_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "elapsed": (datetime.datetime.now() - self.start_time).total_seconds(),
            "event_type": event.type().name,
            "widget_class": obj.__class__.__name__,
            "objectName": obj.objectName() if hasattr(obj, 'objectName') else None,
            "text": obj.text() if hasattr(obj, 'text') else None,
            "window_title": obj.windowTitle() if hasattr(obj, 'windowTitle') else None,
        }
        self.events.append(event_data)

# Global recorder instance
_recorder = WorkflowRecorder()

def workflow_record_start(params):
    """Start recording workflow"""
    if 'workflow_name' not in params:
        return {"success": False, "error": "Missing required parameter: workflow_name"}

    try:
        global _recorder

        if _recorder.recording:
            return {"success": False, "error": "Already recording. Stop current recording first."}

        _recorder.workflow_name = params['workflow_name']
        _recorder.start_time = datetime.datetime.now()
        _recorder.events = []
        _recorder.recording = True

        # Install event filter on QApplication
        QApplication.instance().installEventFilter(_recorder)

        return {
            "success": True,
            "recording": True,
            "workflow_name": _recorder.workflow_name,
            "start_time": _recorder.start_time.isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Implementation approach for workflow.record_stop:**
```python
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer
import os

def layer_add(params):
    """Add vector or raster layer to project"""
    if 'path' not in params:
        return {"success": False, "error": "Missing required parameter: path"}

    try:
        path = params['path']
        name = params.get('name', os.path.basename(path))
        provider = params.get('provider', 'ogr')  # ogr for vector, gdal for raster

        # Determine layer type from extension
        if path.lower().endswith(('.tif', '.tiff', '.jpg', '.png', '.img')):
            layer = QgsRasterLayer(path, name, 'gdal')
        else:
            layer = QgsVectorLayer(path, name, provider)

        if not layer.isValid():
            return {"success": False, "error": f"Layer failed to load: {path}"}

        QgsProject.instance().addMapLayer(layer)

        return {
            "success": True,
            "layer_id": layer.id(),
            "layer_name": layer.name(),
            "layer_type": layer.type().name if hasattr(layer.type(), 'name') else str(layer.type())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Start here:** Follow "Adding a Command" workflow above

**After layer.add, continue with:** layer.remove, layer.set_active, layer.set_visible

---

## 📝 MCP Skills Document (Token-Efficient)

**CRITICAL: This is what AI agents load to learn the tool. MUST be token-efficient.**

**Location:** `qgis_mcp_server/qgis_mcp_skills.md`
**Token Budget:** < 200 tokens (strict limit)
**Update Frequency:** Every new command

**What to include:**
- ✅ Command pattern
- ✅ Discovery commands (help, read_log)
- ✅ Category names with brief command lists
- ✅ Common workflow
- ❌ NO detailed examples (use `help` command instead)
- ❌ NO implementation details
- ❌ NO verbose descriptions

**Why this matters:**
- MCP tools load into EVERY AI conversation
- 50 commands × 150 tokens = 7,500 tokens (BAD)
- 1 pattern + category list = 150 tokens (GOOD)
- Token efficiency = more context for actual work

**Update Rule:**
When you add a command, update the category list in qgis_mcp_skills.md.
If file exceeds 200 tokens, make it MORE concise, not longer.

---

## 🔒 Enforcement Rules

### Code Structure Enforces Pattern

1. **Only ONE route exists:** `/api/command`
2. **Only ONE registry exists:** `COMMAND_REGISTRY.py`
3. **Template must be copied:** Can't deviate from pattern
4. **Registry is required:** Handler doesn't exist until registered

### If You're Tempted To...

- ❌ Add `/api/special_endpoint` → NO, use command router
- ❌ Create new pattern → NO, use template
- ❌ Skip registration → NO, nothing works without registry
- ❌ Skip testing → NO, untested = doesn't exist

---

## 💾 Persistence Across Conversations

### Starting a New Conversation

1. Read this file (IMPLEMENTATION_GUIDE.md)
2. Check COMMAND_REGISTRY.py for what exists
3. Check "Current Status" section
4. Continue from "Next Command to Build"
5. Follow workflow exactly

### This File Is Updated

- After every command is built
- After every test
- After every discovery
- Never skip updates

### Single Source of Truth

**If it's not in this file or COMMAND_REGISTRY.py, it doesn't exist.**

---

## 🎯 Success Metrics

### For Each Command
1. ✅ In registry
2. ✅ Follows template
3. ✅ Curl tested
4. ✅ Visually verified (if UI)
5. ✅ Help entry added
6. ✅ This file updated

### For The Project
1. ✅ One command router working
2. ✅ Pattern documented and enforced
3. ✅ Commands are token-efficient
4. ✅ Any AI can pick up and continue
5. ✅ No repeated explanations needed

---

## 📖 Command Quick Reference

### Lifecycle & Status
```python
qgis.status          # Check QGIS version and platform
qgis.api_status      # Check if API server is running
qgis.reload_plugin   # Reload plugin (delayed 1s)
qgis.restart_api     # Restart API server, kill zombies
qgis.restart         # Restart QGIS (delayed 1s)
```

### Logging & Audit Trail
```python
qgis.log                  # Log message to panel
qgis.read_log             # Read recent log messages (limit: 20)
qgis.read_python_console  # Read Python console (filter: error/warning/all)
```

### UI Discovery & Interaction
```python
widget.list_windows  # List all visible windows
widget.find          # Find widget (type: objectName/title/class/text, value: str)
widget.inspect       # Get widget properties (objectName, include_children)
widget.click         # Click widget (objectName)
widget.wait_for      # Wait for state (state: visible/hidden/enabled/disabled/exists/gone)
```

### Error Detection & Recovery
```python
error.detect         # Detect error dialogs
dialog.close         # Close dialog (objectName or title)
```

### Crash Recovery
```python
crash.save           # Save checkpoint (operation: str)
crash.restore        # Restore checkpoint (checkpoint_id: str)
crash.list           # List all checkpoints
```

### Layer Management (Phase 3)
```python
layer.list           # List all layers (include_metadata: bool)
```

### Discovery (Use First!)
```python
qgis_control({"command": "help"})  # List all commands with examples
qgis_control({"command": "qgis.read_log", "params": {"limit": 10}})  # See what happened
```

---

**Last Updated:** 2026-01-29
**Current Command Count:** 28 commands
**Command Categories:**
  - qgis.* (12):
    - **OS-level** (3): launch, find_process, kill_process
    - **API-level** (9): status, log, read_log, reload_plugin, restart, api_status, restart_api, read_python_console, execute_action
  - crash.* (3): save, restore, list
  - widget.* (8): list_windows, find, inspect, click, wait_for, set_text, select_item, send_keys
  - error.* (1): detect
  - dialog.* (1): close
  - layer.* (1): list
  - workflow.* (5): record_start, record_stop, add_note, list, get
**Status:** ✅ Phase 1 & 2 & A.1 Complete, 🎥 Phase A.2 (Record OilFlow2D Workflows) Next
**New Strategy:** OilFlow2D proof of concept FIRST, then generalize
**Roadmap (REVISED):**
  - **Phase A (NEW PRIORITY):** Workflow recording system (4-5 commands) → Record OilFlow2D workflows → Test automation → Target: 28-29 commands
  - **Phase B:** Implement OilFlow2D-critical commands (discovered via workflows) → Target: ~35 commands
  - Phase C (Essential GIS): Remaining layer/project/canvas commands → Target: ~45 commands
  - Phase D (Data Processing): Geoprocessing and features → Target: ~52 commands
  - Phase E (Output/Export): Data export → Target: ~55 commands
  - Future Phases: Styling, layouts, plugin management → Target: 60-65 total
**Next Up:** workflow.record_start (Build workflow recording system for OilFlow2D automation)
**Architecture:** Single unified qgis-control MCP (no qgis-visual needed)
**Known Limitation:** qgis.read_python_console widget detection is complex. Use qgis.read_log for diagnostics instead.
**VS Code Setup:** See VSCODE_SETUP.md for Cline/Codex configuration instructions
**Pattern Status:** ✅ FOUNDATION COMPLETE
**Two-Sided Implementation:** ✅ ENFORCED (MCP server + QGIS plugin)
**Audit Trail:** ✅ WORKING (all commands auto-log to QGIS panel)
**Self-Management:** ✅ WORKING (can reload itself via MCP)
**Token-Efficient Skills Doc:** ✅ CREATED (qgis_mcp_server/qgis_mcp_skills.md, <200 tokens)
**Autonomous Operation:** ✅ READY (discovery, interaction, wait, error detect, recovery)
**Important:** qgis.reload_plugin clears widget_commands module cache (added 2026-01-29)
**Cleanup:** ✅ Done (removed 12 obsolete files)
**Core Files:**
  - api_server.py (command router + audit trail)
  - COMMAND_REGISTRY.py (single source of truth)
  - COMMAND_TEMPLATE.py (enforces pattern)
  - qgis_mcp_skills.md (AI learning, token-efficient)
**Test:** qgis_control({"command": "qgis.read_log", "params": {"limit": 5}})
