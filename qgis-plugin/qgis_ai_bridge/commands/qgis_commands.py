"""QGIS lifecycle commands"""

def qgis_status(params):
    """Check QGIS status and version"""
    try:
        from qgis.core import Qgis
        from qgis.utils import iface
        import platform

        return {
            "success": True,
            "running": True,
            "version": Qgis.version(),
            "platform": platform.system()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def qgis_log(params):
    """
    Log a message to QGIS message panel

    Args:
        params (dict): Command parameters
            - message (str): Message to log
            - level (str, optional): Log level (info/warning/error), defaults to info

    Returns:
        dict: {"success": bool, "level": str}
    """
    if 'message' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: message"
        }

    try:
        from qgis.core import QgsMessageLog, Qgis
        from ..utils import log_buffer

        message = params['message']
        level_str = params.get('level', 'info').lower()

        # Map string level to Qgis enum
        level_map = {
            'info': Qgis.Info,
            'warning': Qgis.Warning,
            'error': Qgis.Critical
        }

        level = level_map.get(level_str, Qgis.Info)

        # Log to QGIS panel
        QgsMessageLog.logMessage(message, 'QGIS AI Bridge', level)

        # Also store in buffer for reading back
        log_buffer.add_message(message, level_str, 'QGIS AI Bridge')

        return {
            "success": True,
            "level": level_str
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def qgis_read_log(params):
    """
    Read recent messages from QGIS log buffer

    Args:
        params (dict): Command parameters
            - category (str, optional): Log category to filter, defaults to "QGIS AI Bridge"
            - limit (int, optional): Number of recent messages to return, defaults to 20

    Returns:
        dict: {"success": bool, "messages": list, "count": int}
    """
    try:
        from ..utils import log_buffer

        category = params.get('category', 'QGIS AI Bridge')
        limit = params.get('limit', 20)

        # Get messages from buffer
        messages = log_buffer.get_messages(category=category, limit=limit)

        return {
            "success": True,
            "messages": messages,
            "count": len(messages),
            "category": category
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def qgis_reload_plugin(params):
    """
    Reload a QGIS plugin

    Args:
        params (dict): Command parameters
            - plugin_name (str, optional): Plugin to reload, defaults to "qgis_ai_bridge"

    Returns:
        dict: {"success": bool, "plugin": str, "reloading": bool}
    """
    try:
        import sys
        from qgis.utils import reloadPlugin
        from PyQt5.QtCore import QTimer

        plugin_name = params.get('plugin_name', 'qgis_ai_bridge')

        # Schedule reload after delay to allow response to be sent
        def do_reload():
            # Clear module cache for the plugin
            modules_to_clear = [
                plugin_name,
                f'{plugin_name}.api_server',
                f'{plugin_name}.COMMAND_REGISTRY',
                f'{plugin_name}.commands',
                f'{plugin_name}.commands.qgis_commands',
                f'{plugin_name}.commands.crash_commands',
                f'{plugin_name}.commands.widget_commands',
                f'{plugin_name}.utils',
                f'{plugin_name}.utils.log_buffer',
            ]

            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Reload the plugin
            reloadPlugin(plugin_name)

        QTimer.singleShot(1000, do_reload)  # 1 second delay

        return {
            "success": True,
            "plugin": plugin_name,
            "reloading": True,
            "note": "Plugin will reload in 1 second"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def qgis_restart(params):
    """
    Restart QGIS application

    Args:
        params (dict): Command parameters
            - save_project (bool, optional): Save project before restart, defaults to True

    Returns:
        dict: {"success": bool, "restarting": bool}
    """
    try:
        from qgis.core import QgsProject
        from qgis.utils import iface
        from PyQt5.QtCore import QTimer
        import sys
        import subprocess

        save_project = params.get('save_project', True)

        # Save project if requested and it has a file path
        project = QgsProject.instance()
        if save_project and project.fileName():
            project.write()

        # Get QGIS executable path
        qgis_exe = sys.executable.replace('python.exe', 'qgis-ltr-bin.exe')

        # Schedule restart after a short delay to allow response to be sent
        def do_restart():
            # Launch new QGIS instance
            subprocess.Popen([qgis_exe])
            # Exit current instance
            iface.actionExit().trigger()

        QTimer.singleShot(1000, do_restart)  # 1 second delay

        return {
            "success": True,
            "restarting": True,
            "saved": save_project and bool(project.fileName())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def qgis_api_status(params):
    """
    Check API server status

    Args:
        params (dict): No parameters required

    Returns:
        dict: {"success": bool, "api_running": bool, "port": int, "host": str}
    """
    try:
        from qgis.utils import plugins

        # Get the plugin instance
        if 'qgis_ai_bridge' not in plugins:
            return {
                "success": True,
                "api_running": False,
                "error": "Plugin not loaded"
            }

        plugin = plugins['qgis_ai_bridge']

        # Check if API server exists and is running
        if hasattr(plugin, 'api_server') and plugin.api_server:
            return {
                "success": True,
                "api_running": plugin.api_server.is_running(),
                "port": plugin.api_server.port,
                "host": plugin.api_server.host
            }
        else:
            return {
                "success": True,
                "api_running": False,
                "error": "API server not initialized"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def qgis_read_python_console(params):
    """
    Read output from QGIS Python console

    Args:
        params (dict): Command parameters
            - limit (int, optional): Number of recent lines to return, defaults to 50
            - filter (str, optional): Filter for 'error', 'warning', or 'all', defaults to 'all'

    Returns:
        dict: {"success": bool, "output": str, "lines": list}
    """
    try:
        from qgis.utils import iface
        from PyQt5.QtWidgets import QWidget

        limit = params.get('limit', 50)
        filter_type = params.get('filter', 'all').lower()

        # Try to access Python console via QGIS API
        try:
            from console.console import _console
            if _console and hasattr(_console, 'shell'):
                # Get shell widget and its output
                shell = _console.shell
                output_widget = None

                # Search for output widget in shell
                for child in shell.findChildren(QWidget):
                    class_name = child.__class__.__name__
                    if 'Shell' in class_name or 'Output' in class_name or 'Text' in class_name:
                        if hasattr(child, 'toPlainText') or hasattr(child, 'text'):
                            output_widget = child
                            break

                if output_widget:
                    if hasattr(output_widget, 'toPlainText'):
                        full_text = output_widget.toPlainText()
                    else:
                        full_text = output_widget.text()

                    # Process output
                    all_lines = full_text.split('\n')

                    # Filter if needed
                    if filter_type == 'error':
                        filtered_lines = [line for line in all_lines if 'error' in line.lower() or 'exception' in line.lower() or 'traceback' in line.lower()]
                    elif filter_type == 'warning':
                        filtered_lines = [line for line in all_lines if 'warning' in line.lower()]
                    else:
                        filtered_lines = all_lines

                    # Get recent lines
                    recent_lines = filtered_lines[-limit:] if limit else filtered_lines

                    return {
                        "success": True,
                        "output": '\n'.join(recent_lines),
                        "lines": recent_lines,
                        "total_lines": len(all_lines),
                        "method": "console_api"
                    }
        except ImportError:
            pass

        # Fallback: Try widget-based access
        console_dock = iface.mainWindow().findChild(QWidget, 'PythonConsole')

        if not console_dock:
            return {
                "success": False,
                "error": "Python console not found. Open it via Plugins > Python Console"
            }

        # Recursively search for text widgets
        def find_text_widgets(widget):
            found = []
            for child in widget.findChildren(QWidget):
                class_name = child.__class__.__name__
                if hasattr(child, 'toPlainText') or hasattr(child, 'text'):
                    found.append(child)
            return found

        text_widgets = find_text_widgets(console_dock)

        if not text_widgets:
            return {
                "success": False,
                "error": "Console text widget not found. Console may be minimized or not fully loaded."
            }

        # Try each widget until we get content
        for widget in text_widgets:
            try:
                if hasattr(widget, 'toPlainText'):
                    full_text = widget.toPlainText()
                else:
                    full_text = widget.text()

                if full_text and len(full_text) > 10:  # Has substantial content
                    all_lines = full_text.split('\n')

                    # Filter if needed
                    if filter_type == 'error':
                        filtered_lines = [line for line in all_lines if 'error' in line.lower() or 'exception' in line.lower() or 'traceback' in line.lower()]
                    elif filter_type == 'warning':
                        filtered_lines = [line for line in all_lines if 'warning' in line.lower()]
                    else:
                        filtered_lines = all_lines

                    # Get recent lines
                    recent_lines = filtered_lines[-limit:] if limit else filtered_lines

                    return {
                        "success": True,
                        "output": '\n'.join(recent_lines),
                        "lines": recent_lines,
                        "total_lines": len(all_lines),
                        "method": "widget_search"
                    }
            except:
                continue

        return {
            "success": False,
            "error": "Could not read console text from any widget"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def qgis_restart_api(params):
    """
    Restart the API server (stops and starts)

    Args:
        params (dict): No parameters required

    Returns:
        dict: {"success": bool, "restarted": bool, "port": int}
    """
    try:
        from qgis.utils import plugins
        import subprocess
        import time

        # Get the plugin instance
        if 'qgis_ai_bridge' not in plugins:
            return {
                "success": False,
                "error": "Plugin not loaded"
            }

        plugin = plugins['qgis_ai_bridge']

        if not hasattr(plugin, 'api_server') or not plugin.api_server:
            return {
                "success": False,
                "error": "API server not initialized"
            }

        port = plugin.api_server.port

        # Stop the server
        plugin.api_server.stop()
        time.sleep(0.5)  # Brief pause

        # Kill any zombie processes on the port
        try:
            # Get PIDs using the port
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.stdout:
                # Extract PIDs and kill them
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        except:
                            pass
        except:
            pass  # Not critical if this fails

        time.sleep(0.5)  # Brief pause after cleanup

        # Start the server
        plugin.api_server.start()

        return {
            "success": True,
            "restarted": True,
            "port": port,
            "running": plugin.api_server.is_running()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def qgis_execute_action(params):
    """
    Execute a QGIS action by name (menu items, toolbar actions, etc.)

    Args:
        params (dict): Command parameters
            - action_name (str): Name of the action to execute
              Common actions:
              - 'showPythonDialog' - Open Python console
              - 'mActionNewProject' - New project
              - 'mActionOpenProject' - Open project
              - 'mActionSaveProject' - Save project
              - 'mActionShowPluginManager' - Plugin manager
              - 'mActionOptions' - Settings
            - wait (float, optional): Time to wait after execution (seconds), defaults to 0.5

    Returns:
        dict: {
            "success": bool,
            "action_name": str,
            "executed": bool,
            "found": bool
        }
    """
    if 'action_name' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: action_name"
        }

    try:
        from qgis.utils import iface
        from PyQt5.QtWidgets import QApplication
        import time

        action_name = params['action_name']
        wait_time = params.get('wait', 0.5)

        # Get the main window
        main_window = iface.mainWindow()

        # Find the action by object name
        action = main_window.findChild(object, action_name)

        if action is None:
            # Try finding in all actions
            for child_action in main_window.findChildren(object):
                if hasattr(child_action, 'objectName') and child_action.objectName() == action_name:
                    action = child_action
                    break

        if action is None:
            return {
                "success": False,
                "action_name": action_name,
                "found": False,
                "executed": False,
                "error": f"Action '{action_name}' not found"
            }

        # Execute the action
        if hasattr(action, 'trigger'):
            action.trigger()
        elif hasattr(action, 'activate'):
            from PyQt5.QtWidgets import QAction
            action.activate(QAction.Trigger)
        else:
            return {
                "success": False,
                "action_name": action_name,
                "found": True,
                "executed": False,
                "error": "Action found but has no trigger method"
            }

        # Process events to ensure action completes
        QApplication.processEvents()

        # Wait if specified
        if wait_time > 0:
            time.sleep(wait_time)
            QApplication.processEvents()

        return {
            "success": True,
            "action_name": action_name,
            "found": True,
            "executed": True
        }
    except Exception as e:
        return {
            "success": False,
            "action_name": params.get('action_name', 'unknown'),
            "error": str(e)
        }
