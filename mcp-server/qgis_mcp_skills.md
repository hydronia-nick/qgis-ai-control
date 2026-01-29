# QGIS Control MCP Tool

## Pattern
```python
qgis_control({"command": "category.action", "params": {...}})
```

## Discovery
```python
qgis_control({"command": "help"})  # Full reference
qgis_control({"command": "qgis.find_process"})  # Check if QGIS running
qgis_control({"command": "qgis.read_log", "params": {"limit": 10}})  # Recent actions
```

## Categories

**qgis.*** - Lifecycle & Control
  - OS-level: launch, find_process, kill_process
  - API-level: status, log, read_log, reload_plugin, restart, api_status, restart_api, execute_action
**crash.*** - Recovery (save, restore, list)
**widget.*** - UI Control (list_windows, find, inspect, click, wait_for)
**error.*** - Error Detection (detect)
**dialog.*** - Dialog Management (close)

## Autonomous Lifecycle
1. `qgis.find_process` - Check if running
2. `qgis.launch` - Start QGIS if needed (OS-level, works without QGIS)
3. `qgis.status` - Verify API online (waits for plugin to load)
4. Execute commands
5. `qgis.kill_process` - Stop QGIS if needed

## Notes
- **Unified MCP:** One server handles both OS-level (launch) and API commands (widget control)
- Every API command auto-logs to audit trail
- Read audit trail with `qgis.read_log`
- Plugin can reload itself with `qgis.reload_plugin`
