"""
COMMAND REGISTRY - Single source of truth for all commands

This file is the ONLY place where commands are registered.
To add a new command:
1. Create handler in commands/[category]_commands.py
2. Import it here
3. Add to COMMANDS dict
4. Add to HELP dict
5. Test it
6. Update IMPLEMENTATION_GUIDE.md

DO NOT create commands anywhere else.
"""

# Import command handlers
from .commands.qgis_commands import (
    qgis_status, qgis_log, qgis_read_log, qgis_reload_plugin,
    qgis_restart, qgis_api_status, qgis_restart_api, qgis_read_python_console,
    qgis_execute_action
)
from .commands.crash_commands import crash_save, crash_restore, crash_list
from .commands.widget_commands import (
    widget_list_windows, widget_find, widget_inspect, widget_click,
    widget_wait_for, error_detect, dialog_close,
    widget_set_text, widget_select_item, widget_send_keys
)
from .commands.layer_commands import layer_list
from .commands.workflow_commands import (
    workflow_record_start, workflow_record_stop, workflow_add_note,
    workflow_list, workflow_get
)

# COMMANDS - Maps command strings to handler functions
COMMANDS = {
    "qgis.status": qgis_status,
    "qgis.log": qgis_log,
    "qgis.read_log": qgis_read_log,
    "qgis.reload_plugin": qgis_reload_plugin,
    "qgis.restart": qgis_restart,
    "qgis.api_status": qgis_api_status,
    "qgis.restart_api": qgis_restart_api,
    "qgis.read_python_console": qgis_read_python_console,
    "qgis.execute_action": qgis_execute_action,
    "crash.save": crash_save,
    "crash.restore": crash_restore,
    "crash.list": crash_list,
    "widget.list_windows": widget_list_windows,
    "widget.find": widget_find,
    "widget.inspect": widget_inspect,
    "widget.click": widget_click,
    "widget.wait_for": widget_wait_for,
    "widget.set_text": widget_set_text,
    "widget.select_item": widget_select_item,
    "widget.send_keys": widget_send_keys,
    "error.detect": error_detect,
    "dialog.close": dialog_close,
    "layer.list": layer_list,
    "workflow.record_start": workflow_record_start,
    "workflow.record_stop": workflow_record_stop,
    "workflow.add_note": workflow_add_note,
    "workflow.list": workflow_list,
    "workflow.get": workflow_get,
}


# HELP - Provides help text for all commands
HELP = {
    "qgis.status": {
        "params": {},
        "returns": {"running": "bool", "version": "str", "platform": "str"},
        "example": {"command": "qgis.status"},
        "description": "Check QGIS status and version"
    },
    "qgis.log": {
        "params": {
            "message": "str (required)",
            "level": "str (optional: info/warning/error)"
        },
        "returns": {
            "success": "bool",
            "level": "str"
        },
        "example": {
            "command": "qgis.log",
            "params": {
                "message": "Test message",
                "level": "info"
            }
        },
        "description": "Log a message to QGIS message panel"
    },
    "qgis.read_log": {
        "params": {
            "category": "str (optional: defaults to 'QGIS AI Bridge')",
            "limit": "int (optional: defaults to 20)"
        },
        "returns": {
            "success": "bool",
            "messages": "list",
            "count": "int"
        },
        "example": {
            "command": "qgis.read_log",
            "params": {
                "limit": 10
            }
        },
        "description": "Read recent log messages from buffer"
    },
    "qgis.reload_plugin": {
        "params": {
            "plugin_name": "str (optional: defaults to 'qgis_ai_bridge')"
        },
        "returns": {
            "success": "bool",
            "plugin": "str",
            "reloaded": "bool",
            "cleared_modules": "int"
        },
        "example": {
            "command": "qgis.reload_plugin",
            "params": {
                "plugin_name": "qgis_ai_bridge"
            }
        },
        "description": "Reload a QGIS plugin (clears module cache and reloads)"
    },
    "qgis.restart": {
        "params": {
            "save_project": "bool (optional: defaults to True)"
        },
        "returns": {
            "success": "bool",
            "restarting": "bool",
            "saved": "bool"
        },
        "example": {
            "command": "qgis.restart",
            "params": {
                "save_project": True
            }
        },
        "description": "Restart QGIS application (WARNING: This will close and reopen QGIS)"
    },
    "qgis.api_status": {
        "params": {},
        "returns": {
            "success": "bool",
            "api_running": "bool",
            "port": "int",
            "host": "str"
        },
        "example": {
            "command": "qgis.api_status"
        },
        "description": "Check if API server is running"
    },
    "qgis.restart_api": {
        "params": {},
        "returns": {
            "success": "bool",
            "restarted": "bool",
            "port": "int",
            "running": "bool"
        },
        "example": {
            "command": "qgis.restart_api"
        },
        "description": "Restart API server (kills zombie processes and restarts)"
    },
    "qgis.read_python_console": {
        "params": {
            "limit": "int (optional: defaults to 50)",
            "filter": "str (optional: 'error', 'warning', 'all', defaults to 'all')"
        },
        "returns": {
            "success": "bool",
            "output": "str",
            "lines": "list",
            "total_lines": "int"
        },
        "example": {
            "command": "qgis.read_python_console",
            "params": {
                "limit": 20,
                "filter": "error"
            }
        },
        "description": "Read output from QGIS Python console (for debugging)"
    },
    "qgis.execute_action": {
        "params": {
            "action_name": "str (required: action name like 'showPythonDialog', 'mActionNewProject')",
            "wait": "float (optional: time to wait after execution in seconds, defaults to 0.5)"
        },
        "returns": {
            "success": "bool",
            "action_name": "str",
            "found": "bool",
            "executed": "bool"
        },
        "example": {
            "command": "qgis.execute_action",
            "params": {
                "action_name": "showPythonDialog"
            }
        },
        "description": "Execute QGIS menu/toolbar action by name (e.g., open Python console, new project)"
    },
    "crash.save": {
        "params": {
            "operation": "str (required)"
        },
        "returns": {
            "success": "bool",
            "checkpoint_id": "str",
            "project_path": "str"
        },
        "example": {
            "command": "crash.save",
            "params": {
                "operation": "opening risky dialog"
            }
        },
        "description": "Save QGIS state before risky operations"
    },
    "crash.restore": {
        "params": {
            "checkpoint_id": "str (required)"
        },
        "returns": {
            "success": "bool",
            "restored": "bool",
            "project_path": "str"
        },
        "example": {
            "command": "crash.restore",
            "params": {
                "checkpoint_id": "checkpoint_20260129_143022"
            }
        },
        "description": "Restore QGIS state from checkpoint"
    },
    "crash.list": {
        "params": {},
        "returns": {
            "success": "bool",
            "checkpoints": "list",
            "count": "int"
        },
        "example": {
            "command": "crash.list"
        },
        "description": "List all saved checkpoints"
    },
    "widget.list_windows": {
        "params": {
            "visible_only": "bool (optional: defaults to True)"
        },
        "returns": {
            "success": "bool",
            "windows": "list",
            "count": "int"
        },
        "example": {
            "command": "widget.list_windows"
        },
        "description": "List all top-level windows/dialogs with details"
    },
    "widget.find": {
        "params": {
            "type": "str (required: 'objectName', 'title', 'class', 'text')",
            "value": "str (required: search value)",
            "parent": "str (optional: parent objectName)",
            "exact": "bool (optional: exact match, defaults to False)"
        },
        "returns": {
            "success": "bool",
            "widgets": "list",
            "count": "int"
        },
        "example": {
            "command": "widget.find",
            "params": {
                "type": "title",
                "value": "New Project"
            }
        },
        "description": "Find widgets by objectName, title, class, or text"
    },
    "widget.inspect": {
        "params": {
            "objectName": "str (required: widget to inspect)",
            "include_children": "bool (optional: defaults to False)"
        },
        "returns": {
            "success": "bool",
            "widget": "dict",
            "children": "list"
        },
        "example": {
            "command": "widget.inspect",
            "params": {
                "objectName": "QPushButton_create",
                "include_children": True
            }
        },
        "description": "Get detailed properties of a widget"
    },
    "widget.click": {
        "params": {
            "objectName": "str (required: widget to click)",
            "button": "str (optional: 'left', 'right', 'middle', defaults to 'left')"
        },
        "returns": {
            "success": "bool",
            "clicked": "bool",
            "widget_class": "str"
        },
        "example": {
            "command": "widget.click",
            "params": {
                "objectName": "QPushButton_ok"
            }
        },
        "description": "Click a widget programmatically"
    },
    "widget.wait_for": {
        "params": {
            "objectName": "str (optional: widget to wait for)",
            "type": "str (optional: search type if not using objectName)",
            "value": "str (optional: search value if not using objectName)",
            "state": "str (required: 'visible', 'hidden', 'enabled', 'disabled', 'exists', 'gone')",
            "timeout": "int (optional: timeout in seconds, defaults to 5)"
        },
        "returns": {
            "success": "bool",
            "condition_met": "bool",
            "elapsed_time": "float"
        },
        "example": {
            "command": "widget.wait_for",
            "params": {
                "objectName": "dlg_new_project",
                "state": "visible",
                "timeout": 5
            }
        },
        "description": "Wait for widget to appear/disappear or reach a certain state"
    },
    "widget.set_text": {
        "params": {
            "objectName": "str (required: widget to set text in)",
            "text": "str (required: text to set)",
            "clear_first": "bool (optional: clear existing text first, defaults to True)"
        },
        "returns": {
            "success": "bool",
            "widget_class": "str",
            "text_set": "str",
            "objectName": "str"
        },
        "example": {
            "command": "widget.set_text",
            "params": {
                "objectName": "lineEdit_search",
                "text": "Hello World"
            }
        },
        "description": "Set text in a text input widget (QLineEdit, QTextEdit, QPlainTextEdit)"
    },
    "widget.select_item": {
        "params": {
            "objectName": "str (required: widget to select from)",
            "value": "str or int (required: item text or index to select)",
            "by_index": "bool (optional: select by index instead of text, defaults to False)"
        },
        "returns": {
            "success": "bool",
            "widget_class": "str",
            "selected": "str or int",
            "current_text": "str",
            "objectName": "str"
        },
        "example": {
            "command": "widget.select_item",
            "params": {
                "objectName": "comboBox_projection",
                "value": "EPSG:4326"
            }
        },
        "description": "Select an item in a dropdown/combobox/listbox"
    },
    "widget.send_keys": {
        "params": {
            "objectName": "str (optional: widget to send keys to, if None sends globally)",
            "keys": "str (required: keys to send, e.g., 'Ctrl+S', 'Enter', 'text')",
            "delay": "float (optional: delay between key presses in seconds, defaults to 0.1)"
        },
        "returns": {
            "success": "bool",
            "keys_sent": "str",
            "target": "str"
        },
        "example": {
            "command": "widget.send_keys",
            "params": {
                "keys": "Ctrl+S"
            }
        },
        "description": "Send keyboard input to a widget or globally"
    },
    "error.detect": {
        "params": {},
        "returns": {
            "success": "bool",
            "errors": "list",
            "count": "int",
            "has_errors": "bool"
        },
        "example": {
            "command": "error.detect"
        },
        "description": "Detect error dialogs currently visible"
    },
    "dialog.close": {
        "params": {
            "objectName": "str (optional: dialog to close)",
            "title": "str (optional: dialog title if not using objectName)",
            "force": "bool (optional: force close, defaults to False)"
        },
        "returns": {
            "success": "bool",
            "closed": "bool",
            "method": "str"
        },
        "example": {
            "command": "dialog.close",
            "params": {
                "title": "Error"
            }
        },
        "description": "Close a dialog by objectName or title"
    },
    "layer.list": {
        "params": {
            "include_metadata": "bool (optional: include detailed metadata, defaults to True)"
        },
        "returns": {
            "success": "bool",
            "layers": "list",
            "count": "int"
        },
        "example": {
            "command": "layer.list",
            "params": {
                "include_metadata": True
            }
        },
        "description": "List all layers in current QGIS project with metadata"
    },
    "workflow.record_start": {
        "params": {
            "workflow_name": "str (required: name for the workflow)",
            "description": "str (optional: brief description of workflow purpose)"
        },
        "returns": {
            "success": "bool",
            "recording": "bool",
            "workflow_name": "str",
            "start_time": "str"
        },
        "example": {
            "command": "workflow.record_start",
            "params": {
                "workflow_name": "oilflow2d_new_project",
                "description": "Create new OilFlow2D project"
            }
        },
        "description": "Start recording workflow interactions (clicks, keyboard, dialogs)"
    },
    "workflow.record_stop": {
        "params": {},
        "returns": {
            "success": "bool",
            "workflow_name": "str",
            "event_count": "int",
            "duration": "float",
            "file_path": "str"
        },
        "example": {
            "command": "workflow.record_stop"
        },
        "description": "Stop recording and generate workflow documentation"
    },
    "workflow.add_note": {
        "params": {
            "note": "str (required: annotation text)"
        },
        "returns": {
            "success": "bool",
            "note": "str"
        },
        "example": {
            "command": "workflow.add_note",
            "params": {
                "note": "This sets the output coordinate system"
            }
        },
        "description": "Add manual annotation to current workflow recording"
    },
    "workflow.list": {
        "params": {},
        "returns": {
            "success": "bool",
            "workflows": "list",
            "count": "int"
        },
        "example": {
            "command": "workflow.list"
        },
        "description": "List all saved workflows"
    },
    "workflow.get": {
        "params": {
            "workflow_name": "str (required: name of workflow to retrieve)"
        },
        "returns": {
            "success": "bool",
            "workflow_name": "str",
            "content": "str",
            "file_path": "str"
        },
        "example": {
            "command": "workflow.get",
            "params": {
                "workflow_name": "oilflow2d_new_project"
            }
        },
        "description": "Get specific workflow content for AI to follow"
    },
}


def get(command):
    """
    Get handler function for a command

    Args:
        command (str): Command string like "qgis.status"

    Returns:
        function: Handler function or None if not found
    """
    return COMMANDS.get(command)


def list_commands():
    """
    List all available command strings

    Returns:
        list: List of command strings
    """
    return list(COMMANDS.keys())


def get_help(command=None):
    """
    Get help for one or all commands

    Args:
        command (str, optional): Specific command to get help for

    Returns:
        dict: Help information
    """
    if command:
        if command in HELP:
            return HELP[command]
        else:
            return {
                "error": f"Command not found: {command}",
                "available": list_commands()
            }
    else:
        return {
            "commands": HELP,
            "count": len(COMMANDS),
            "categories": list(set(cmd.split('.')[0] for cmd in COMMANDS.keys()))
        }


def validate_command(command):
    """
    Validate that a command exists

    Args:
        command (str): Command string

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not command:
        return False, "Command cannot be empty"

    if '.' not in command:
        return False, "Command must be in format 'category.action'"

    if command not in COMMANDS:
        return False, f"Unknown command: {command}. Available: {list_commands()}"

    return True, None
