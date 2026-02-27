import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from config.db import mongodb_connection, check_mongodb_connection
from extensions import socketio

# Import blueprints
from routes.auth import auth_bp
from routes.quiz import quiz_bp
from routes.duel import duel_bp

load_dotenv("key.env")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

CORS(app, supports_credentials=True, resources={r"/*": {"origins": allowed_origins}})

socketio.init_app(
    app,
    cors_allowed_origins=allowed_origins,
    async_mode='eventlet'
)

# ─── Register HTTP blueprints ─────────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(duel_bp)

# ─── Health ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "QuizApp API running"})

@app.route('/health')
def health():
    ok, msg = check_mongodb_connection()
    return jsonify({"mongodb": ok, "message": msg}), 200 if ok else 503

# ─── Socket.IO — Duel real-time ───────────────────────────────────────────────

def get_db():
    return mongodb_connection().get_database("hackathon_db")

@socketio.on('connect')
def on_connect():
    print(f"[socket] connected: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    print(f"[socket] disconnected: {request.sid}")

@socketio.on('duel:join_room')
def on_join_duel_room(data):
    """
    Client joins a duel room after creating or being redirected to play.
    data = { duel_id: str }
    Server emits back duel:started if duel is already in_battle.
    """
    from flask_socketio import join_room, emit
    duel_id = data.get('duel_id')
    if not duel_id:
        return

    join_room(duel_id)
    print(f"[socket] {request.sid} joined room {duel_id}")

    # If duel already started (player 2 joined via HTTP before socket connected)
    try:
        from bson import ObjectId
        duel = get_db().duels.find_one({"_id": ObjectId(duel_id)})
        if duel and duel.get('status') == 'in_battle':
            emit('duel:started', {"duel_id": duel_id}, to=duel_id)
    except Exception as e:
        print(f"[socket] join_room check error: {e}")

@socketio.on('duel:answer_submitted')
def on_answer_submitted(data):
    """
    Notify the room when a player finishes answering.
    data = { duel_id, player_id, score, both_done }
    """
    from flask_socketio import emit
    duel_id = data.get('duel_id')
    if not duel_id:
        return
    emit('duel:progress', data, to=duel_id)
    if data.get('both_done'):
        emit('duel:finished', data, to=duel_id)

# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
