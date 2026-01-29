# QGIS AI Bridge - Testing Guide

**CRITICAL: ALL testing MUST go through MCP, never bypass with direct curl**

---

## Why MCP Testing is Mandatory

This entire project is designed for AI agents to control QGIS via MCP. Testing directly via curl bypasses the MCP layer and doesn't validate the production flow:

❌ **Wrong:** `curl http://localhost:5557/api/command -d '{"command":"..."}'`
✅ **Right:** Use MCP tool `qgis_control` with `{"command":"...", "params":{...}}`

## Setup Requirements

### 1. MCP Server Configuration

**Location:** `C:\Users\PC\AppData\Roaming\Claude\claude_desktop_config.json`

**Required configuration:**
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

**After adding/changing:** Restart Claude Desktop

### 2. Verify MCP Server is Available

In Claude Desktop or VS Code with Claude, the MCP tool should appear as:
- Tool name: `qgis_control` (or `mcp__qgis-control__qgis_control` in some environments)

## Testing Workflow

### Step 1: Check if QGIS is Running

```python
qgis_control({
    "command": "qgis.find_process"
})
```

**Expected:** `{"success": true, "running": true/false, "processes": [...], "count": N}`

### Step 2: Launch QGIS if Needed

```python
qgis_control({
    "command": "qgis.launch"
})
```

**Expected:** `{"success": true, "pid": 12345, "message": "QGIS launched with PID..."}`

**Wait 10-15 seconds for QGIS to fully load**

### Step 3: Verify API is Online

```python
qgis_control({
    "command": "qgis.status"
})
```

**Expected:** `{"success": true, "running": true, "version": "3.40.7-Bratislava", "platform": "Windows"}`

### Step 4: Test Your Command

```python
qgis_control({
    "command": "workflow.record_start",
    "params": {
        "workflow_name": "test_workflow",
        "description": "Testing recording system"
    }
})
```

**Expected:** `{"success": true, "recording": true, "workflow_name": "test_workflow", "start_time": "..."}`

### Step 5: Verify in Audit Log

```python
qgis_control({
    "command": "qgis.read_log",
    "params": {"limit": 5}
})
```

**Expected:** Should show your command in the audit trail with ✓ checkmark

## Testing Checklist for New Commands

Before marking a command as complete:

- [ ] **MCP Test:** Command works via `qgis_control` MCP tool
- [ ] **Success Case:** Returns expected result with `"success": true`
- [ ] **Error Case:** Returns `"success": false, "error": "..."` for invalid params
- [ ] **Audit Log:** Command appears in `qgis.read_log` output
- [ ] **Help Entry:** Command appears in `qgis_control({"command": "help"})` output
- [ ] **Documentation:** Command added to IMPLEMENTATION_GUIDE.md working commands
- [ ] **Visual Verification:** If UI command, manually verify it did what it claims

## Common Testing Patterns

### Test Error Handling
```python
# Missing required parameter
qgis_control({
    "command": "workflow.record_start",
    "params": {}  # Missing workflow_name
})
# Expected: {"success": false, "error": "Missing required parameter: workflow_name"}
```

### Test with Invalid Data
```python
# Non-existent workflow
qgis_control({
    "command": "workflow.get",
    "params": {"workflow_name": "doesnt_exist"}
})
# Expected: {"success": false, "error": "Workflow 'doesnt_exist' not found"}
```

### Test Command Chaining
```python
# Start recording
qgis_control({"command": "workflow.record_start", "params": {"workflow_name": "test"}})

# Add note
qgis_control({"command": "workflow.add_note", "params": {"note": "Test note"}})

# Stop recording
qgis_control({"command": "workflow.record_stop"})

# Verify it was saved
qgis_control({"command": "workflow.list"})
```

## Debugging Failed Tests

### MCP Tool Not Available

**Symptom:** "Unknown tool: qgis_control" or tool not in list

**Solution:**
1. Check `claude_desktop_config.json` has qgis-control entry
2. Restart Claude Desktop
3. Verify MCP server path is correct
4. Check Python is in PATH and can run server.py

### Connection Refused

**Symptom:** "Failed to connect to localhost:5557"

**Solution:**
1. Check QGIS is running: `qgis.find_process`
2. Launch QGIS: `qgis.launch`
3. Wait 10-15 seconds for plugin to load
4. Try again

### Command Not Found

**Symptom:** "Unknown command: workflow.record_start"

**Solution:**
1. Check command is in COMMAND_REGISTRY.py
2. Reload plugin: `qgis.reload_plugin`
3. If reload doesn't work, restart QGIS:
   - `qgis_control({"command": "qgis.find_process"})`
   - Kill process manually or use OS tools
   - `qgis_control({"command": "qgis.launch"})`

### Plugin Not Loading

**Symptom:** Commands fail, API not responding

**Solution:**
1. Check QGIS Python console for errors
2. Use `qgis.read_python_console` to see plugin load errors
3. Fix errors and reload or restart QGIS

## Never Do This

❌ **Direct curl:** `curl http://localhost:5557/api/command ...`
❌ **Skip MCP:** Testing only the QGIS API endpoint
❌ **Manual only:** Only testing commands manually in QGIS UI
❌ **No verification:** Not checking audit log or help output

## Always Do This

✅ **Via MCP:** Use `qgis_control` tool exclusively
✅ **Full flow:** Test OS commands (launch) → API commands (your command)
✅ **Verify logging:** Check `qgis.read_log` shows command executed
✅ **Document:** Update IMPLEMENTATION_GUIDE.md with working example
✅ **Error cases:** Test missing params, invalid values
✅ **Help updated:** Verify command shows in help output

---

## Quick Test Template

```python
# 1. Verify QGIS is running
qgis_control({"command": "qgis.status"})

# 2. Test your new command
qgis_control({
    "command": "your.new_command",
    "params": {"param1": "value1"}
})

# 3. Check it was logged
qgis_control({"command": "qgis.read_log", "params": {"limit": 1}})

# 4. Test error case
qgis_control({
    "command": "your.new_command",
    "params": {}  # Missing required params
})

# 5. Verify in help
qgis_control({"command": "help"})
```

---

**Last Updated:** 2026-01-29
**Remember:** If you're not using MCP, you're not testing the real product!
