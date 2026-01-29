"""Flask HTTP API Server - Command Router Pattern"""
import json
import socket
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.serving import make_server
from . import COMMAND_REGISTRY

class APIServer:
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.host = self.config["server"]["host"]
        self.port = self.config["server"]["port"]
        self.app = Flask(__name__)
        CORS(self.app)

        self.server = None
        self.running = False

        self._register_routes()

    def _register_routes(self):
        """Register command router - ONLY route"""

        @self.app.route('/api/command', methods=['POST'])
        def execute_command():
            from qgis.core import QgsMessageLog, Qgis
            from .utils import log_buffer

            data = request.get_json()
            command = data.get('command')
            params = data.get('params', {})

            # Special case: help doesn't need logging
            if command == 'help':
                return jsonify(COMMAND_REGISTRY.get_help())

            # Validate command
            is_valid, error = COMMAND_REGISTRY.validate_command(command)
            if not is_valid:
                msg = f"❌ Invalid command: {command}"
                QgsMessageLog.logMessage(msg, 'QGIS AI Bridge', Qgis.Warning)
                log_buffer.add_message(msg, 'warning', 'QGIS AI Bridge')
                return jsonify({"success": False, "error": error}), 404

            # Execute command
            handler = COMMAND_REGISTRY.get(command)
            result = handler(params)

            # Log command execution (skip logging for qgis.log and qgis.read_log to avoid issues)
            if command not in ['qgis.log', 'qgis.read_log']:
                if result.get('success'):
                    # Format params for log (keep it concise)
                    params_str = f" | params: {params}" if params else ""
                    msg = f"✓ {command}{params_str}"
                    QgsMessageLog.logMessage(msg, 'QGIS AI Bridge', Qgis.Info)
                    log_buffer.add_message(msg, 'info', 'QGIS AI Bridge')
                else:
                    error_msg = result.get('error', 'Unknown error')
                    msg = f"✗ {command} failed: {error_msg}"
                    QgsMessageLog.logMessage(msg, 'QGIS AI Bridge', Qgis.Warning)
                    log_buffer.add_message(msg, 'warning', 'QGIS AI Bridge')

            return jsonify(result)

        @self.app.after_request
        def add_headers(response):
            response.headers['Connection'] = 'close'
            return response

    def start(self):
        if self.running:
            return

        def run_server():
            self.server = make_server(self.host, self.port, self.app, threaded=True)
            self.server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.serve_forever()

        self.running = True
        from threading import Thread
        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.server:
            self.server.shutdown()

    def is_running(self):
        return self.running
