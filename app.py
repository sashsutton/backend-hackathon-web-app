import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from config.db import mongodb_connection, check_mongodb_connection

from routes.auth import auth_bp
from routes.quiz import quiz_bp
from routes.duel import duel_bp

load_dotenv("key.env")

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    }
})

app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(duel_bp)

@app.route('/')
def index():
    return jsonify({"status": "ok"})

@app.route('/health')
def health():
    ok, msg = check_mongodb_connection()
    return jsonify({"mongodb": ok, "message": msg}), 200 if ok else 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
