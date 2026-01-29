"""
Widget finding and introspection utilities
"""

from typing import List, Optional, Dict
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt


class WidgetFinder:
    """Utilities for finding and introspecting Qt widgets"""

    @staticmethod
    def get_widget_tree(root: QWidget = None, include_invisible: bool = False) -> dict:
        """Get complete widget hierarchy as a tree.

        Args:
            root: Root widget (default: main window)
            include_invisible: Include non-visible widgets

        Returns:
            dict representing widget tree
        """
        if root is None:
            # Get QGIS main window
            from qgis.utils import iface
            root = iface.mainWindow()

        def build_tree(widget: QWidget, path: str = "") -> dict:
            """Recursively build widget tree"""
            if not widget:
                return None

            # Skip invisible widgets if requested
            if not include_invisible and not widget.isVisible():
                return None

            object_name = widget.objectName() or f"<{widget.__class__.__name__}>"
            current_path = f"{path}.{object_name}" if path else object_name

            node = {
                "path": current_path,
                "object_name": widget.objectName(),
                "type": widget.__class__.__name__,
                "visible": widget.isVisible(),
                "enabled": widget.isEnabled(),
                "geometry": {
                    "x": widget.x(),
                    "y": widget.y(),
                    "width": widget.width(),
                    "height": widget.height()
                }
            }

            # Get text if available
            if hasattr(widget, 'text'):
                try:
                    text = widget.text()
                    if text:
                        node["text"] = text
                except:
                    pass

            # Get children
            children = []
            for child in widget.children():
                if isinstance(child, QWidget):
                    child_node = build_tree(child, current_path)
                    if child_node:
                        children.append(child_node)

            if children:
                node["children"] = children

            return node

        return build_tree(root)

    @staticmethod
    def find_widgets(criteria: dict, root: QWidget = None, search_all_windows: bool = True) -> List[dict]:
        """Find widgets matching criteria.

        Args:
            criteria: dict with optional keys:
                - object_name: str (exact match or contains)
                - widget_type: str (class name)
                - text_contains: str
                - visible_only: bool (default True)
            root: Root widget to search from
            search_all_windows: If True and root is None, search all top-level widgets including dialogs

        Returns:
            List of matching widgets with their info
        """
        results = []
        visible_only = criteria.get("visible_only", True)

        # If no root specified and search_all_windows is True, search all top-level widgets
        if root is None and search_all_windows:
            roots_to_search = QApplication.topLevelWidgets()
        elif root is None:
            from qgis.utils import iface
            roots_to_search = [iface.mainWindow()]
        else:
            roots_to_search = [root]

        def search_widget(widget: QWidget, path: str = ""):
            """Recursively search for matching widgets"""
            if not widget:
                return

            # Skip invisible if requested
            if visible_only and not widget.isVisible():
                return

            object_name = widget.objectName() or f"<{widget.__class__.__name__}>"
            current_path = f"{path}.{object_name}" if path else object_name

            # Check criteria
            matches = True

            # Check object name
            if "object_name" in criteria:
                search_name = criteria["object_name"]
                if search_name not in object_name:
                    matches = False

            # Check widget type
            if matches and "widget_type" in criteria:
                if widget.__class__.__name__ != criteria["widget_type"]:
                    matches = False

            # Check text
            if matches and "text_contains" in criteria:
                text_match = False
                if hasattr(widget, 'text'):
                    try:
                        text = widget.text()
                        if criteria["text_contains"] in text:
                            text_match = True
                    except:
                        pass
                if not text_match:
                    matches = False

            if matches:
                widget_info = WidgetFinder.get_widget_info(widget, current_path)
                results.append(widget_info)

            # Search children
            for child in widget.children():
                if isinstance(child, QWidget):
                    search_widget(child, current_path)

        # Search all roots
        for root_widget in roots_to_search:
            if root_widget and root_widget.isVisible():
                search_widget(root_widget)

        return results

    @staticmethod
    def get_widget_info(widget: QWidget, path: str = None) -> dict:
        """Get detailed information about a widget.

        Args:
            widget: QWidget instance
            path: Widget path (optional)

        Returns:
            dict with widget information
        """
        from .coordinate_helper import CoordinateHelper

        if not widget:
            return None

        info = {
            "path": path or widget.objectName(),
            "object_name": widget.objectName(),
            "type": widget.__class__.__name__,
            "visible": widget.isVisible(),
            "enabled": widget.isEnabled(),
            "geometry": {
                "x": widget.x(),
                "y": widget.y(),
                "width": widget.width(),
                "height": widget.height()
            }
        }

        # Get screen position
        screen_coords = CoordinateHelper.widget_to_screen(widget)
        if screen_coords:
            info["screen_position"] = {
                "x": screen_coords["screen_x"],
                "y": screen_coords["screen_y"]
            }
            info["screen_center"] = {
                "x": screen_coords["center_x"],
                "y": screen_coords["center_y"]
            }

        # Get text if available
        if hasattr(widget, 'text'):
            try:
                text = widget.text()
                if text:
                    info["text"] = text
            except:
                pass

        # Get value if available (for input widgets)
        if hasattr(widget, 'value'):
            try:
                info["value"] = widget.value()
            except:
                pass

        # Get current text for combo boxes
        if hasattr(widget, 'currentText'):
            try:
                info["current_text"] = widget.currentText()
            except:
                pass

        # Get plain text for text edits
        if hasattr(widget, 'toPlainText'):
            try:
                info["plain_text"] = widget.toPlainText()
            except:
                pass

        return info

    @staticmethod
    def get_widget_by_path(path: str, root: QWidget = None) -> Optional[QWidget]:
        """Get widget by its path.

        Args:
            path: Widget path (e.g., "MainWindow.OilFlow2DDialog.logMessages" or "PluginDialog.button")
            root: Root widget to search from

        Returns:
            QWidget instance or None
        """
        def search_from_root(start_widget, path_parts):
            """Helper to search from a specific root widget"""
            current = start_widget
            # Skip the first part if it matches the root's object name
            start_index = 1 if path_parts and path_parts[0] == start_widget.objectName() else 0

            for part in path_parts[start_index:]:
                found = False
                for child in current.children():
                    if isinstance(child, QWidget):
                        if child.objectName() == part:
                            current = child
                            found = True
                            break
                if not found:
                    return None
            return current

        parts = path.split(".")

        # If root is provided, search only from that root
        if root is not None:
            return search_from_root(root, parts)

        # Try all top-level widgets (dialogs, main window, etc.)
        for toplevel in QApplication.topLevelWidgets():
            if toplevel.isVisible():
                result = search_from_root(toplevel, parts)
                if result:
                    return result

        return None

    @staticmethod
    def list_all_dialogs() -> List[dict]:
        """List all currently open dialogs.

        Returns:
            List of dialog information dicts
        """
        dialogs = []
        for widget in QApplication.topLevelWidgets():
            # Check if it's a dialog and visible
            if widget.isVisible() and widget.windowTitle():
                # Check if it's a dialog (not the main window)
                if widget.windowFlags() & Qt.Dialog:
                    dialogs.append({
                        "title": widget.windowTitle(),
                        "object_name": widget.objectName(),
                        "type": widget.__class__.__name__,
                        "visible": widget.isVisible(),
                        "modal": widget.isModal() if hasattr(widget, 'isModal') else False
                    })

        return dialogs
