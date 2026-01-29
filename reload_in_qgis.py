"""
Reload QGIS AI Bridge plugin - Run this in QGIS Python Console

Usage:
1. Open QGIS Python Console (Ctrl+Alt+P)
2. Copy and paste this entire script
3. Press Enter

This clears the module cache and reloads the plugin.
"""

import sys

# Clear module cache for this plugin
modules_to_clear = [
    'qgis_ai_bridge',
    'qgis_ai_bridge.api_server',
    'qgis_ai_bridge.ai_bridge',
    'qgis_ai_bridge.COMMAND_REGISTRY',
    'qgis_ai_bridge.commands',
    'qgis_ai_bridge.commands.qgis_commands',
]

for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]
        print(f"Cleared: {module}")

# Reload plugin
from qgis.utils import reloadPlugin
reloadPlugin('qgis_ai_bridge')
print("\nPlugin reloaded successfully!")
print("Test with: curl -X POST http://127.0.0.1:5557/api/command -d '{\"command\":\"help\"}'")
