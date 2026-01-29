"""Log buffer for storing recent QGIS AI Bridge log messages"""
from collections import deque
from datetime import datetime

# Circular buffer storing last 100 log messages
_log_buffer = deque(maxlen=100)


def add_message(message, level, category='QGIS AI Bridge'):
    """
    Add a message to the log buffer

    Args:
        message (str): Log message
        level (str): Log level (info/warning/error)
        category (str): Log category
    """
    _log_buffer.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'category': category,
        'message': message
    })


def get_messages(category=None, limit=20):
    """
    Get recent messages from log buffer

    Args:
        category (str, optional): Filter by category
        limit (int): Maximum number of messages to return

    Returns:
        list: Recent log messages
    """
    messages = list(_log_buffer)

    # Filter by category if specified
    if category:
        messages = [m for m in messages if m['category'] == category]

    # Return most recent messages (up to limit)
    return messages[-limit:] if limit else messages


def clear_buffer():
    """Clear all messages from buffer"""
    _log_buffer.clear()
