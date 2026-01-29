"""
COMMAND TEMPLATE - Copy this file for every new command

WORKFLOW:
1. Copy this file to commands/[category]_commands.py
2. Rename function to match command (e.g., dialog_open for "dialog.open")
3. Update docstring with purpose
4. Implement _do_work_internal() with actual logic
5. Add to COMMAND_REGISTRY.py
6. Test with curl
7. Update IMPLEMENTATION_GUIDE.md

DO NOT deviate from this pattern.
"""

def command_template(params):
    """
    [REPLACE: One-line description of what this command does]

    Args:
        params (dict): Command parameters
            - required_param (str): [REPLACE: Description]
            - optional_param (str, optional): [REPLACE: Description]

    Returns:
        dict: Always returns {"success": bool, ...}
            On success: {"success": True, "result": any}
            On failure: {"success": False, "error": str}
    """
    # Step 1: Validate required parameters
    if 'required_param' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: required_param"
        }

    # Step 2: Call internal function (keeps this function clean)
    try:
        result = _do_work_internal(
            params['required_param'],
            params.get('optional_param', 'default_value')
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _do_work_internal(required_param, optional_param):
    """
    Internal function where complex logic lives

    All PyQt5, widget finding, QGIS API calls go here.
    Keep the main handler function simple.

    Args:
        required_param: The required parameter
        optional_param: The optional parameter

    Returns:
        any: The result to return to the caller

    Raises:
        Exception: If anything goes wrong
    """
    # TODO: Implement actual logic here
    #
    # Examples:
    # - from qgis.utils import iface, plugins
    # - from qgis.core import QgsMessageLog, Qgis
    # - from PyQt5.QtWidgets import QApplication, QWidget
    #
    # Keep this function focused and testable
    pass


# Example of a properly implemented command:
#
# def qgis_log(params):
#     """Log a message to QGIS message panel"""
#     if 'message' not in params:
#         return {"success": False, "error": "Missing message"}
#
#     try:
#         result = _log_internal(
#             params['message'],
#             params.get('level', 'info')
#         )
#         return {"success": True, "logged": result}
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
# def _log_internal(message, level):
#     from qgis.core import QgsMessageLog, Qgis
#
#     level_map = {
#         'info': Qgis.Info,
#         'warning': Qgis.Warning,
#         'error': Qgis.Critical
#     }
#
#     qgis_level = level_map.get(level, Qgis.Info)
#     QgsMessageLog.logMessage(message, "AI Bridge", qgis_level)
#     return True
