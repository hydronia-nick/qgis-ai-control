#!/usr/bin/env python3
"""QGIS MCP Server - Unified control for QGIS (OS-level + API)"""
import asyncio
import json
import requests
import subprocess
import time
import psutil
from pathlib import Path
from typing import Any, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", flush=True)
    import sys
    sys.exit(1)

# QGIS paths
QGIS_ROOT = Path(r"C:\Program Files\QGIS 3.40.7")
QGIS_EXE = QGIS_ROOT / "bin" / "qgis-ltr-bin.exe"

# QGIS Plugin API endpoint
QGIS_API = "http://127.0.0.1:5557/api/command"

# Create MCP server
app = Server("qgis-control")


# ========================================
# OS-LEVEL COMMANDS (execute directly)
# ========================================

def qgis_launch(params: dict) -> dict:
    """
    Launch QGIS executable (OS-level command)

    Args:
        params: {
            "project_path": str (optional) - Path to .qgz/.qgs file to open
        }

    Returns:
        {"success": bool, "pid": int, "message": str}
    """
    try:
        args = [str(QGIS_EXE)]
        project_path = params.get("project_path")
        if project_path:
            args.append(project_path)

        process = subprocess.Popen(args)

        # Wait for QGIS to start
        time.sleep(3)

        return {
            "success": True,
            "pid": process.pid,
            "message": f"QGIS launched with PID {process.pid}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def qgis_find_process(params: dict) -> dict:
    """
    Check if QGIS is running (OS-level command)

    Returns:
        {"success": bool, "running": bool, "pids": list, "count": int}
    """
    try:
        qgis_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'qgis' in proc.info['name'].lower():
                    qgis_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "success": True,
            "running": len(qgis_processes) > 0,
            "processes": qgis_processes,
            "count": len(qgis_processes)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def qgis_kill_process(params: dict) -> dict:
    """
    Kill all QGIS processes (OS-level command)

    Returns:
        {"success": bool, "killed": int}
    """
    try:
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'qgis' in proc.info['name'].lower():
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "success": True,
            "killed": killed_count,
            "message": f"Killed {killed_count} QGIS process(es)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# OS-level command registry
OS_COMMANDS = {
    "qgis.launch": qgis_launch,
    "qgis.find_process": qgis_find_process,
    "qgis.kill_process": qgis_kill_process,
}


# ========================================
# MCP TOOL HANDLERS
# ========================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available QGIS control tools"""
    return [
        Tool(
            name="qgis_control",
            description="Control QGIS via commands. Use {command: 'category.action', params: {...}}. Call with command:'help' for full reference. Includes OS-level commands (launch, find_process) and API commands (all others).",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command in format 'category.action' (e.g., 'qgis.launch', 'qgis.status', 'widget.list_windows')"
                    },
                    "params": {
                        "type": "object",
                        "description": "Command-specific parameters"
                    }
                },
                "required": ["command"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute QGIS control command"""
    if name != "qgis_control":
        raise ValueError(f"Unknown tool: {name}")

    command = arguments.get("command")
    params = arguments.get("params", {})

    # Check if this is an OS-level command
    if command in OS_COMMANDS:
        result = OS_COMMANDS[command](params)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    # Otherwise, forward to QGIS API
    try:
        response = requests.post(
            QGIS_API,
            json={"command": command, "params": params},
            timeout=10
        )
        result = response.json()

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
