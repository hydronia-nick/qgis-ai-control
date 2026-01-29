"""Crash recovery commands"""
import json
from datetime import datetime
from pathlib import Path

# In-memory checkpoint storage (survives until QGIS restart)
_checkpoints = {}


def crash_save(params):
    """
    Save QGIS state before risky operations

    Args:
        params (dict): Command parameters
            - operation (str): Description of risky operation about to perform

    Returns:
        dict: {"success": bool, "checkpoint_id": str, "project_path": str}
    """
    if 'operation' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: operation"
        }

    try:
        checkpoint_id, project_path = _save_checkpoint_internal(params['operation'])
        return {
            "success": True,
            "checkpoint_id": checkpoint_id,
            "project_path": project_path,
            "operation": params['operation']
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def crash_restore(params):
    """
    Restore QGIS state after crash or failed operation

    Args:
        params (dict): Command parameters
            - checkpoint_id (str): ID from crash.save

    Returns:
        dict: {"success": bool, "restored": bool, "project_path": str}
    """
    if 'checkpoint_id' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: checkpoint_id"
        }

    try:
        restored, project_path = _restore_checkpoint_internal(params['checkpoint_id'])
        return {
            "success": True,
            "restored": restored,
            "project_path": project_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def crash_list(params):
    """
    List all saved checkpoints

    Args:
        params (dict): No parameters required

    Returns:
        dict: {"success": bool, "checkpoints": list}
    """
    try:
        checkpoints = [
            {
                "checkpoint_id": cid,
                "operation": data["operation"],
                "timestamp": data["timestamp"],
                "project_path": data["project_path"]
            }
            for cid, data in _checkpoints.items()
        ]
        return {
            "success": True,
            "checkpoints": checkpoints,
            "count": len(checkpoints)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _save_checkpoint_internal(operation):
    """
    Save current QGIS state to checkpoint

    Args:
        operation (str): Description of operation

    Returns:
        tuple: (checkpoint_id, project_path)
    """
    from qgis.core import QgsProject

    project = QgsProject.instance()
    project_path = project.fileName() or "[Unsaved Project]"

    # Generate checkpoint ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_id = f"checkpoint_{timestamp}"

    # Store checkpoint data
    _checkpoints[checkpoint_id] = {
        "checkpoint_id": checkpoint_id,
        "timestamp": timestamp,
        "operation": operation,
        "project_path": project_path,
        "is_dirty": project.isDirty()
    }

    return checkpoint_id, project_path


def _restore_checkpoint_internal(checkpoint_id):
    """
    Restore QGIS state from checkpoint

    Args:
        checkpoint_id (str): Checkpoint to restore

    Returns:
        tuple: (restored: bool, project_path: str)
    """
    if checkpoint_id not in _checkpoints:
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")

    checkpoint = _checkpoints[checkpoint_id]
    project_path = checkpoint["project_path"]

    # For now, just return checkpoint info
    # Future: Could reload project, restore window state, etc.
    return True, project_path
