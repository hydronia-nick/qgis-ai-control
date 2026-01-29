"""
Coordinate conversion utilities for widget positioning
"""

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QWidget


class CoordinateHelper:
    """Helper for converting between widget and screen coordinates"""

    @staticmethod
    def widget_to_screen(widget: QWidget) -> dict:
        """Convert widget position to screen coordinates.

        Args:
            widget: QWidget instance

        Returns:
            dict with screen_x, screen_y, width, height
        """
        if not widget:
            return None

        # Get widget geometry
        rect = widget.geometry()

        # Convert to global/screen coordinates
        global_pos = widget.mapToGlobal(QPoint(0, 0))

        return {
            "screen_x": global_pos.x(),
            "screen_y": global_pos.y(),
            "width": rect.width(),
            "height": rect.height(),
            "center_x": global_pos.x() + rect.width() // 2,
            "center_y": global_pos.y() + rect.height() // 2
        }

    @staticmethod
    def get_widget_center(widget: QWidget) -> tuple:
        """Get the center point of a widget in screen coordinates.

        Args:
            widget: QWidget instance

        Returns:
            tuple (x, y) of center point in screen coordinates
        """
        coords = CoordinateHelper.widget_to_screen(widget)
        if coords:
            return (coords["center_x"], coords["center_y"])
        return None

    @staticmethod
    def is_point_in_widget(widget: QWidget, screen_x: int, screen_y: int) -> bool:
        """Check if a screen coordinate is within a widget's bounds.

        Args:
            widget: QWidget instance
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate

        Returns:
            True if point is within widget bounds
        """
        coords = CoordinateHelper.widget_to_screen(widget)
        if not coords:
            return False

        return (coords["screen_x"] <= screen_x <= coords["screen_x"] + coords["width"] and
                coords["screen_y"] <= screen_y <= coords["screen_y"] + coords["height"])
