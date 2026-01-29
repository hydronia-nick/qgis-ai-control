"""
QGIS AI Bridge Plugin - Main Plugin Class
"""

import logging
import sys
from pathlib import Path

from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsMessageLog, Qgis

from .api_server import APIServer


logger = logging.getLogger("qgis_ai_bridge")


class QgisAiBridge:
    """Main QGIS AI Bridge Plugin Class"""

    def __init__(self, iface):
        """Constructor.

        Args:
            iface: QgisInterface instance
        """
        self.iface = iface
        self.plugin_dir = Path(__file__).parent
        self.api_server = None

        # Initialize logging
        QgsMessageLog.logMessage(
            "QGIS AI Bridge initializing...",
            "AI Bridge",
            Qgis.Info
        )

    def initGui(self):
        """Initialize the plugin GUI"""
        # Create menu action
        self.action = QAction(
            "Start AI Bridge Server",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.toggle_server)

        # Add to Plugins menu
        self.iface.addPluginToMenu("AI Bridge", self.action)

        # Log initialization
        QgsMessageLog.logMessage(
            "QGIS AI Bridge GUI initialized",
            "AI Bridge",
            Qgis.Info
        )

        # Auto-start server
        self.start_server()

    def unload(self):
        """Cleanup when plugin is unloaded"""
        # Stop server
        self.stop_server()

        # Remove menu item
        self.iface.removePluginMenu("AI Bridge", self.action)

        # Clear module cache for hot reload
        self._clear_module_cache()

        QgsMessageLog.logMessage(
            "QGIS AI Bridge unloaded",
            "AI Bridge",
            Qgis.Info
        )

    def _clear_module_cache(self):
        """Clear Python module cache for this plugin to enable hot reload"""
        try:
            # Find all modules that belong to this plugin
            plugin_modules = [
                module_name for module_name in sys.modules.keys()
                if module_name.startswith('qgis_ai_bridge')
            ]

            # Remove them from sys.modules
            for module_name in plugin_modules:
                del sys.modules[module_name]

            QgsMessageLog.logMessage(
                f"Cleared {len(plugin_modules)} cached modules for hot reload",
                "AI Bridge",
                Qgis.Info
            )
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error clearing module cache: {str(e)}",
                "AI Bridge",
                Qgis.Warning
            )

    def start_server(self):
        """Start the HTTP API server"""
        if self.api_server and self.api_server.is_running():
            QgsMessageLog.logMessage(
                "API Server already running",
                "AI Bridge",
                Qgis.Warning
            )
            return

        try:
            # Create and start server
            config_path = self.plugin_dir / "config.json"
            self.api_server = APIServer(config_path)
            self.api_server.start()

            # Update action text
            if hasattr(self, 'action'):
                self.action.setText("Stop AI Bridge Server")

            # Log success
            QgsMessageLog.logMessage(
                f"API Server started on http://{self.api_server.host}:{self.api_server.port}",
                "AI Bridge",
                Qgis.Success
            )

            # Show message bar
            self.iface.messageBar().pushMessage(
                "AI Bridge",
                f"API Server started on port {self.api_server.port}",
                Qgis.Success,
                duration=3
            )

        except Exception as e:
            error_msg = f"Failed to start API Server: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "AI Bridge", Qgis.Critical)

            # Show error dialog
            QMessageBox.critical(
                self.iface.mainWindow(),
                "AI Bridge Error",
                error_msg
            )

    def stop_server(self):
        """Stop the HTTP API server"""
        if not self.api_server or not self.api_server.is_running():
            QgsMessageLog.logMessage(
                "API Server not running",
                "AI Bridge",
                Qgis.Warning
            )
            return

        try:
            self.api_server.stop()

            # Update action text
            if hasattr(self, 'action'):
                self.action.setText("Start AI Bridge Server")

            QgsMessageLog.logMessage(
                "API Server stopped",
                "AI Bridge",
                Qgis.Info
            )

            # Show message bar
            self.iface.messageBar().pushMessage(
                "AI Bridge",
                "API Server stopped",
                Qgis.Info,
                duration=3
            )

        except Exception as e:
            error_msg = f"Failed to stop API Server: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "AI Bridge", Qgis.Critical)

    def toggle_server(self):
        """Toggle server on/off"""
        if self.api_server and self.api_server.is_running():
            self.stop_server()
        else:
            self.start_server()
