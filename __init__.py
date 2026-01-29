"""
QGIS AI Bridge Plugin

AI-native automation framework for QGIS testing, debugging, and documentation.
"""


def classFactory(iface):
    """Load QgisAiBridge class from ai_bridge module.

    Args:
        iface: QgisInterface instance

    Returns:
        QgisAiBridge plugin instance
    """
    from .ai_bridge import QgisAiBridge
    return QgisAiBridge(iface)
