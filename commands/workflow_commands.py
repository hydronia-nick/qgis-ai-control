"""
Workflow recording commands for QGIS AI Bridge

Handles workflow recording: record_start, record_stop, add_note, list, get
Records user interactions (clicks, keyboard, dialogs) and generates workflow documentation
"""

import os
import json
import datetime
from pathlib import Path
from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QApplication


class WorkflowRecorder(QObject):
    """Event filter to capture significant Qt events for workflow documentation"""

    def __init__(self):
        super().__init__()
        self.recording = False
        self.events = []
        self.workflow_name = None
        self.workflow_description = None
        self.start_time = None

    def eventFilter(self, obj, event):
        """Filter Qt events and log significant ones"""
        if not self.recording:
            return False

        # Capture significant events only
        event_type = event.type()

        if event_type in [
            QEvent.MouseButtonPress,  # Clicks
            QEvent.Show,              # Dialog/widget appears
            QEvent.Hide,              # Dialog/widget closes
            QEvent.FocusIn,           # Widget receives focus
        ]:
            self.log_event(obj, event)

        # Keyboard events - only for text input widgets
        elif event_type == QEvent.KeyPress:
            # Only log for input widgets to reduce noise
            widget_class = obj.__class__.__name__
            if widget_class in ['QLineEdit', 'QTextEdit', 'QPlainTextEdit', 'QComboBox']:
                self.log_event(obj, event)

        return False  # Don't block events, just observe

    def log_event(self, obj, event):
        """Log event with widget properties and context"""
        try:
            elapsed = (datetime.datetime.now() - self.start_time).total_seconds()

            # Get event type name
            event_type = event.type()
            event_name = None

            # Map event types to readable names
            event_map = {
                QEvent.MouseButtonPress: "click",
                QEvent.Show: "show",
                QEvent.Hide: "hide",
                QEvent.FocusIn: "focus",
                QEvent.KeyPress: "key_press"
            }
            event_name = event_map.get(event_type, f"event_{event_type}")

            # Get widget properties
            widget_class = obj.__class__.__name__
            object_name = obj.objectName() if hasattr(obj, 'objectName') else ""

            # Get widget text/title
            widget_text = None
            if hasattr(obj, 'text'):
                try:
                    widget_text = obj.text()
                except:
                    pass

            # Get window title for dialogs
            window_title = None
            if hasattr(obj, 'windowTitle'):
                try:
                    window_title = obj.windowTitle()
                except:
                    pass

            # Get parent window info for context
            parent_window = None
            try:
                window = obj.window()
                if window and window != obj:
                    parent_window = {
                        "class": window.__class__.__name__,
                        "objectName": window.objectName() if hasattr(window, 'objectName') else "",
                        "title": window.windowTitle() if hasattr(window, 'windowTitle') else ""
                    }
            except:
                pass

            # Build event data
            event_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "elapsed": round(elapsed, 3),
                "event": event_name,
                "widget": {
                    "class": widget_class,
                    "objectName": object_name,
                    "text": widget_text,
                    "windowTitle": window_title
                },
                "parent_window": parent_window
            }

            # Add specific event details
            if event_type == QEvent.MouseButtonPress:
                button = event.button()
                button_map = {1: "left", 2: "right", 4: "middle"}
                event_data["button"] = button_map.get(button, "unknown")

            elif event_type == QEvent.KeyPress:
                event_data["key"] = event.text()

            self.events.append(event_data)

        except Exception as e:
            # Don't let logging errors break the application
            print(f"WorkflowRecorder error: {e}")

    def add_note(self, note):
        """Add a manual annotation to the workflow"""
        if not self.recording:
            return False

        try:
            elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
            self.events.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "elapsed": round(elapsed, 3),
                "event": "note",
                "note": note
            })
            return True
        except Exception as e:
            print(f"WorkflowRecorder add_note error: {e}")
            return False


# Global recorder instance
_recorder = WorkflowRecorder()


def workflow_record_start(params):
    """
    Start recording workflow interactions

    Args:
        params (dict): Command parameters
            - workflow_name (str, required): Name for the workflow
            - description (str, optional): Brief description of workflow purpose

    Returns:
        dict: {
            "success": bool,
            "recording": bool,
            "workflow_name": str,
            "start_time": str
        }
    """
    if 'workflow_name' not in params:
        return {"success": False, "error": "Missing required parameter: workflow_name"}

    try:
        global _recorder

        if _recorder.recording:
            return {
                "success": False,
                "error": "Already recording. Stop current recording first with workflow.record_stop"
            }

        # Initialize recording
        _recorder.workflow_name = params['workflow_name']
        _recorder.workflow_description = params.get('description', '')
        _recorder.start_time = datetime.datetime.now()
        _recorder.events = []
        _recorder.recording = True

        # Install event filter on QApplication to capture all events
        app = QApplication.instance()
        app.installEventFilter(_recorder)
        QApplication.processEvents()

        return {
            "success": True,
            "recording": True,
            "workflow_name": _recorder.workflow_name,
            "start_time": _recorder.start_time.isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def workflow_record_stop(params):
    """
    Stop recording and generate workflow documentation

    Args:
        params (dict): Command parameters (none required)

    Returns:
        dict: {
            "success": bool,
            "workflow_name": str,
            "event_count": int,
            "duration": float,
            "file_path": str
        }
    """
    try:
        global _recorder

        if not _recorder.recording:
            return {
                "success": False,
                "error": "Not currently recording. Start recording with workflow.record_start"
            }

        # Stop recording
        _recorder.recording = False

        # Remove event filter
        app = QApplication.instance()
        app.removeEventFilter(_recorder)

        # Calculate duration
        end_time = datetime.datetime.now()
        duration = (end_time - _recorder.start_time).total_seconds()

        # Generate workflow document
        workflow_dir = Path(__file__).parent.parent / "mcp-server" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflow_dir / f"{_recorder.workflow_name}.md"

        # Generate markdown content
        markdown = generate_workflow_markdown(
            _recorder.workflow_name,
            _recorder.workflow_description,
            _recorder.events,
            _recorder.start_time,
            duration
        )

        # Write to file
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        # Also save raw JSON for debugging
        json_file = workflow_dir / f"{_recorder.workflow_name}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "workflow_name": _recorder.workflow_name,
                "description": _recorder.workflow_description,
                "start_time": _recorder.start_time.isoformat(),
                "duration": duration,
                "events": _recorder.events
            }, f, indent=2)

        result = {
            "success": True,
            "workflow_name": _recorder.workflow_name,
            "event_count": len(_recorder.events),
            "duration": round(duration, 2),
            "file_path": str(workflow_file),
            "json_path": str(json_file)
        }

        # Reset recorder
        _recorder.events = []
        _recorder.workflow_name = None
        _recorder.workflow_description = None
        _recorder.start_time = None

        QApplication.processEvents()

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def workflow_add_note(params):
    """
    Add a manual annotation to the current recording

    Args:
        params (dict): Command parameters
            - note (str, required): Annotation text

    Returns:
        dict: {
            "success": bool,
            "note": str
        }
    """
    if 'note' not in params:
        return {"success": False, "error": "Missing required parameter: note"}

    try:
        global _recorder

        if not _recorder.recording:
            return {
                "success": False,
                "error": "Not currently recording. Start recording with workflow.record_start"
            }

        note_added = _recorder.add_note(params['note'])

        if note_added:
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

            return {
                "success": True,
                "note": params['note']
            }
        else:
            return {
                "success": False,
                "error": "Failed to add note"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_workflow_markdown(workflow_name, description, events, start_time, duration):
    """Generate markdown documentation from recorded events"""

    # Group events into logical steps
    steps = []
    current_step = []

    for i, event in enumerate(events):
        current_step.append(event)

        # Start new step on significant events
        if event['event'] in ['click', 'show', 'note']:
            if len(current_step) > 1:
                steps.append(current_step[:-1])
                current_step = [event]

    # Add remaining events
    if current_step:
        steps.append(current_step)

    # Build markdown
    md = f"""# Workflow: {workflow_name}

**Purpose:** {description or "No description provided"}
**Recorded:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {duration:.1f} seconds
**Steps:** {len(steps)}

---

## Steps

"""

    for step_num, step_events in enumerate(steps, 1):
        # Get primary event (usually first or last in group)
        primary = step_events[-1] if step_events[-1]['event'] != 'focus' else step_events[0]

        md += f"### {step_num}. "

        # Generate step title from event
        if primary['event'] == 'note':
            md += f"Note: {primary['note']}\n"
            md += f"- **Time:** {primary['elapsed']}s\n"

        elif primary['event'] == 'click':
            widget = primary['widget']
            md += f"Click {widget['class']}"
            if widget['text']:
                md += f" '{widget['text']}'"
            md += "\n"
            md += f"- **Time:** {primary['elapsed']}s\n"
            md += f"- **Command:** widget.click\n"
            if widget['objectName']:
                md += f"- **Target:** objectName=\"{widget['objectName']}\"\n"
            if widget['text']:
                md += f"- **Text:** \"{widget['text']}\"\n"

        elif primary['event'] == 'show':
            widget = primary['widget']
            md += f"Dialog/Window Opened"
            if widget['windowTitle']:
                md += f": {widget['windowTitle']}"
            md += "\n"
            md += f"- **Time:** {primary['elapsed']}s\n"
            if widget['objectName']:
                md += f"- **ObjectName:** {widget['objectName']}\n"
            if widget['windowTitle']:
                md += f"- **Title:** {widget['windowTitle']}\n"

        elif primary['event'] == 'key_press':
            widget = primary['widget']
            md += f"Enter text in {widget['class']}\n"
            md += f"- **Time:** {primary['elapsed']}s\n"
            md += f"- **Command:** widget.set_text\n"
            if widget['objectName']:
                md += f"- **Target:** objectName=\"{widget['objectName']}\"\n"
            md += f"- **Value:** <user_provided>\n"

        md += "\n"

    md += """---

## Notes

- Review and edit this workflow before using
- Add wait times where needed (widget.wait_for)
- Add verification steps for critical dialogs
- Replace hardcoded values with <user_provided> variables
- Add troubleshooting section for common issues

---

## Raw Events

For detailed event inspection, see the accompanying .json file.
"""

    return md


def workflow_list(params):
    """
    List all saved workflows

    Args:
        params (dict): Command parameters (none required)

    Returns:
        dict: {
            "success": bool,
            "workflows": list,
            "count": int
        }
    """
    try:
        workflow_dir = Path(__file__).parent.parent / "mcp-server" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflows = []
        for md_file in workflow_dir.glob("*.md"):
            if md_file.name == "README.md":
                continue

            # Read first few lines for metadata
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            name = md_file.stem
            purpose = ""
            recorded = ""

            for line in lines:
                if line.startswith("**Purpose:**"):
                    purpose = line.replace("**Purpose:**", "").strip()
                elif line.startswith("**Recorded:**"):
                    recorded = line.replace("**Recorded:**", "").strip()

            workflows.append({
                "name": name,
                "purpose": purpose,
                "recorded": recorded,
                "file_path": str(md_file)
            })

        QApplication.processEvents()

        return {
            "success": True,
            "workflows": workflows,
            "count": len(workflows)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def workflow_get(params):
    """
    Get specific workflow content

    Args:
        params (dict): Command parameters
            - workflow_name (str, required): Name of workflow to retrieve

    Returns:
        dict: {
            "success": bool,
            "workflow_name": str,
            "content": str
        }
    """
    if 'workflow_name' not in params:
        return {"success": False, "error": "Missing required parameter: workflow_name"}

    try:
        workflow_name = params['workflow_name']
        workflow_dir = Path(__file__).parent.parent / "mcp-server" / "workflows"
        workflow_file = workflow_dir / f"{workflow_name}.md"

        if not workflow_file.exists():
            return {
                "success": False,
                "error": f"Workflow '{workflow_name}' not found"
            }

        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()

        QApplication.processEvents()

        return {
            "success": True,
            "workflow_name": workflow_name,
            "content": content,
            "file_path": str(workflow_file)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
