"""Widget control commands - Programmatic UI interaction via PyQt5"""


def widget_list_windows(params):
    """
    List all top-level windows/dialogs

    Args:
        params (dict): Command parameters
            - visible_only (bool, optional): Only return visible windows, defaults to True

    Returns:
        dict: {"success": bool, "windows": list, "count": int}
    """
    try:
        from PyQt5.QtWidgets import QApplication

        visible_only = params.get('visible_only', True)
        windows = []

        for widget in QApplication.topLevelWidgets():
            if visible_only and not widget.isVisible():
                continue

            windows.append({
                "class": widget.__class__.__name__,
                "title": widget.windowTitle(),
                "objectName": widget.objectName(),
                "visible": widget.isVisible(),
                "enabled": widget.isEnabled(),
                "modal": widget.isModal() if hasattr(widget, 'isModal') else False,
                "geometry": {
                    "x": widget.x(),
                    "y": widget.y(),
                    "width": widget.width(),
                    "height": widget.height()
                }
            })

        return {
            "success": True,
            "windows": windows,
            "count": len(windows)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def widget_find(params):
    """
    Find widget(s) by objectName, title, or class

    Args:
        params (dict): Command parameters
            - type (str): Search type - 'objectName', 'title', 'class', 'text'
            - value (str): Value to search for
            - parent (str, optional): Parent widget objectName to search within
            - exact (bool, optional): Exact match vs contains, defaults to False

    Returns:
        dict: {"success": bool, "widgets": list, "count": int}
    """
    if 'type' not in params or 'value' not in params:
        return {
            "success": False,
            "error": "Missing required parameters: type and value"
        }

    try:
        from PyQt5.QtWidgets import QApplication

        search_type = params['type']
        search_value = params['value']
        parent_name = params.get('parent')
        exact = params.get('exact', False)

        matches = []

        # Determine search root
        if parent_name:
            # Find parent first
            root_widgets = [w for w in QApplication.topLevelWidgets()
                          if w.objectName() == parent_name]
            if not root_widgets:
                return {
                    "success": False,
                    "error": f"Parent widget not found: {parent_name}"
                }
        else:
            root_widgets = QApplication.topLevelWidgets()

        # Search recursively
        def search_widget(widget, depth=0):
            # Check current widget
            match = False
            if search_type == 'objectName':
                widget_value = widget.objectName()
            elif search_type == 'title':
                widget_value = widget.windowTitle()
            elif search_type == 'class':
                widget_value = widget.__class__.__name__
            elif search_type == 'text':
                widget_value = widget.text() if hasattr(widget, 'text') else ''
            else:
                return

            if exact:
                match = widget_value == search_value
            else:
                match = search_value.lower() in widget_value.lower()

            if match:
                matches.append({
                    "class": widget.__class__.__name__,
                    "objectName": widget.objectName(),
                    "title": widget.windowTitle() if hasattr(widget, 'windowTitle') else '',
                    "text": widget.text() if hasattr(widget, 'text') else '',
                    "visible": widget.isVisible(),
                    "enabled": widget.isEnabled(),
                    "depth": depth
                })

            # Search children
            if hasattr(widget, 'children'):
                for child in widget.children():
                    if hasattr(child, 'isVisible'):  # Only QWidgets
                        search_widget(child, depth + 1)

        for root in root_widgets:
            search_widget(root)

        return {
            "success": True,
            "widgets": matches,
            "count": len(matches),
            "search": {
                "type": search_type,
                "value": search_value,
                "exact": exact
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def widget_inspect(params):
    """
    Get detailed properties of a specific widget

    Args:
        params (dict): Command parameters
            - objectName (str): Widget objectName to inspect
            - include_children (bool, optional): Include child widgets, defaults to False

    Returns:
        dict: {"success": bool, "widget": dict, "children": list}
    """
    if 'objectName' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: objectName"
        }

    try:
        from PyQt5.QtWidgets import QApplication

        object_name = params['objectName']
        include_children = params.get('include_children', False)

        # Find the widget
        widget = None
        for w in QApplication.allWidgets():
            if w.objectName() == object_name:
                widget = w
                break

        if not widget:
            return {
                "success": False,
                "error": f"Widget not found: {object_name}"
            }

        # Get properties
        properties = {
            "class": widget.__class__.__name__,
            "objectName": widget.objectName(),
            "visible": widget.isVisible(),
            "enabled": widget.isEnabled(),
            "geometry": {
                "x": widget.x(),
                "y": widget.y(),
                "width": widget.width(),
                "height": widget.height()
            },
            "size": {
                "width": widget.width(),
                "height": widget.height(),
                "minimumWidth": widget.minimumWidth(),
                "minimumHeight": widget.minimumHeight()
            }
        }

        # Add type-specific properties
        if hasattr(widget, 'windowTitle'):
            properties['title'] = widget.windowTitle()
        if hasattr(widget, 'text'):
            properties['text'] = widget.text()
        if hasattr(widget, 'isChecked'):
            properties['checked'] = widget.isChecked()
        if hasattr(widget, 'currentText'):
            properties['currentText'] = widget.currentText()
        if hasattr(widget, 'placeholderText'):
            properties['placeholderText'] = widget.placeholderText()
        if hasattr(widget, 'toolTip'):
            properties['toolTip'] = widget.toolTip()

        result = {
            "success": True,
            "widget": properties
        }

        # Include children if requested
        if include_children:
            children = []
            for child in widget.children():
                if hasattr(child, 'objectName'):
                    children.append({
                        "class": child.__class__.__name__,
                        "objectName": child.objectName(),
                        "visible": child.isVisible() if hasattr(child, 'isVisible') else False,
                        "enabled": child.isEnabled() if hasattr(child, 'isEnabled') else False
                    })
            result['children'] = children
            result['child_count'] = len(children)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def widget_click(params):
    """
    Click a widget programmatically

    Args:
        params (dict): Command parameters
            - objectName (str): Widget objectName to click
            - button (str, optional): Mouse button - 'left', 'right', 'middle', defaults to 'left'

    Returns:
        dict: {"success": bool, "clicked": bool, "widget_class": str}
    """
    if 'objectName' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: objectName"
        }

    try:
        from PyQt5.QtWidgets import QApplication, QPushButton, QToolButton, QAbstractButton
        from PyQt5.QtCore import Qt, QPoint
        from PyQt5.QtTest import QTest

        object_name = params['objectName']
        button_name = params.get('button', 'left')

        # Map button names to Qt constants
        button_map = {
            'left': Qt.LeftButton,
            'right': Qt.RightButton,
            'middle': Qt.MiddleButton
        }
        button = button_map.get(button_name, Qt.LeftButton)

        # Find the widget
        widget = None
        for w in QApplication.allWidgets():
            if w.objectName() == object_name:
                widget = w
                break

        if not widget:
            return {
                "success": False,
                "error": f"Widget not found: {object_name}"
            }

        if not widget.isVisible():
            return {
                "success": False,
                "error": f"Widget is not visible: {object_name}"
            }

        if not widget.isEnabled():
            return {
                "success": False,
                "error": f"Widget is not enabled: {object_name}"
            }

        # Click the widget
        widget_class = widget.__class__.__name__

        # For buttons, use click() method if available
        if isinstance(widget, QAbstractButton):
            widget.click()
        else:
            # For other widgets, use QTest to simulate mouse click
            QTest.mouseClick(widget, button, Qt.NoModifier, QPoint(widget.width()//2, widget.height()//2))

        return {
            "success": True,
            "clicked": True,
            "widget_class": widget_class,
            "objectName": object_name
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def widget_wait_for(params):
    """
    Wait for widget to appear/disappear or reach a certain state

    Args:
        params (dict): Command parameters
            - objectName (str, optional): Widget objectName to wait for (if checking specific widget)
            - type (str, optional): Search type for finding widget - 'objectName', 'title', 'class'
            - value (str, optional): Search value (alternative to objectName)
            - state (str): State to wait for - 'visible', 'hidden', 'enabled', 'disabled', 'exists', 'gone'
            - timeout (int, optional): Timeout in seconds, defaults to 5

    Returns:
        dict: {"success": bool, "condition_met": bool, "elapsed_time": float}
    """
    if 'state' not in params:
        return {
            "success": False,
            "error": "Missing required parameter: state"
        }

    if 'objectName' not in params and ('type' not in params or 'value' not in params):
        return {
            "success": False,
            "error": "Must provide either objectName OR (type and value)"
        }

    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer, QEventLoop
        import time

        state = params['state']
        timeout = params.get('timeout', 5)
        object_name = params.get('objectName')
        search_type = params.get('type')
        search_value = params.get('value')

        start_time = time.time()
        poll_interval = 0.1  # Check every 100ms

        def check_condition():
            # Find widget
            widget = None

            if object_name:
                for w in QApplication.allWidgets():
                    if w.objectName() == object_name:
                        widget = w
                        break
            else:
                # Use search
                for w in QApplication.allWidgets():
                    if search_type == 'class' and w.__class__.__name__ == search_value:
                        widget = w
                        break
                    elif search_type == 'title' and hasattr(w, 'windowTitle') and search_value in w.windowTitle():
                        widget = w
                        break

            # Check state
            if state == 'exists':
                return widget is not None
            elif state == 'gone':
                return widget is None
            elif widget is None:
                return False
            elif state == 'visible':
                return widget.isVisible()
            elif state == 'hidden':
                return not widget.isVisible()
            elif state == 'enabled':
                return widget.isEnabled()
            elif state == 'disabled':
                return not widget.isEnabled()
            else:
                return False

        # Poll until condition met or timeout
        while time.time() - start_time < timeout:
            if check_condition():
                return {
                    "success": True,
                    "condition_met": True,
                    "elapsed_time": time.time() - start_time,
                    "state": state
                }

            # Process events to keep UI responsive
            QApplication.processEvents()
            time.sleep(poll_interval)

        # Timeout
        return {
            "success": True,
            "condition_met": False,
            "elapsed_time": time.time() - start_time,
            "state": state,
            "timeout": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def error_detect(params):
    """
    Detect error dialogs currently visible

    Args:
        params (dict): Command parameters (no parameters required)

    Returns:
        dict: {"success": bool, "errors": list, "count": int}
    """
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog

        errors = []

        # Check all top-level widgets for error dialogs
        for widget in QApplication.topLevelWidgets():
            if not widget.isVisible():
                continue

            is_error = False
            error_info = {
                "class": widget.__class__.__name__,
                "objectName": widget.objectName(),
                "title": widget.windowTitle() if hasattr(widget, 'windowTitle') else '',
            }

            # Check if it's a QMessageBox
            if isinstance(widget, QMessageBox):
                is_error = True
                error_info["type"] = "QMessageBox"
                error_info["text"] = widget.text() if hasattr(widget, 'text') else ''
                error_info["icon"] = widget.icon() if hasattr(widget, 'icon') else None

            # Check for error keywords in title
            elif isinstance(widget, QDialog):
                title_lower = error_info["title"].lower()
                if any(keyword in title_lower for keyword in ['error', 'warning', 'failed', 'exception']):
                    is_error = True
                    error_info["type"] = "Dialog with error keyword"

            if is_error:
                errors.append(error_info)

        return {
            "success": True,
            "errors": errors,
            "count": len(errors),
            "has_errors": len(errors) > 0
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def dialog_close(params):
    """
    Close a dialog by objectName or title

    Args:
        params (dict): Command parameters
            - objectName (str, optional): Dialog objectName to close
            - title (str, optional): Dialog title to close (if objectName not provided)
            - force (bool, optional): Force close even if dialog is modal, defaults to False

    Returns:
        dict: {"success": bool, "closed": bool, "method": str}
    """
    if 'objectName' not in params and 'title' not in params:
        return {
            "success": False,
            "error": "Must provide either objectName or title"
        }

    try:
        from PyQt5.QtWidgets import QApplication, QDialog

        object_name = params.get('objectName')
        title = params.get('title')
        force = params.get('force', False)

        # Find the dialog
        dialog = None
        for widget in QApplication.topLevelWidgets():
            if object_name and widget.objectName() == object_name:
                dialog = widget
                break
            elif title and hasattr(widget, 'windowTitle') and title in widget.windowTitle():
                dialog = widget
                break

        if not dialog:
            return {
                "success": False,
                "error": f"Dialog not found: {object_name or title}"
            }

        # Try different close methods
        method_used = None

        # Method 1: Try reject() if it's a QDialog
        if isinstance(dialog, QDialog) and hasattr(dialog, 'reject'):
            dialog.reject()
            method_used = "reject()"

        # Method 2: Try close()
        elif hasattr(dialog, 'close'):
            dialog.close()
            method_used = "close()"

        # Method 3: Force close with deleteLater
        elif force:
            dialog.deleteLater()
            method_used = "deleteLater()"
        else:
            return {
                "success": False,
                "error": "No suitable close method found"
            }

        # Process events to ensure close happens
        QApplication.processEvents()

        return {
            "success": True,
            "closed": True,
            "method": method_used,
            "dialog": object_name or title
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
