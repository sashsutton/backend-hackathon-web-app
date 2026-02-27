"""
Shared Flask extensions — import socketio from here in routes
to avoid circular imports.
"""
from flask_socketio import SocketIO

socketio = SocketIO()
