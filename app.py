import os
from clerk_backend_api import Clerk
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from config.db import mongodb_connection, check_mongodb_connection
from services.clerk_auth import ClerkAuthService

# Import blueprints
from routes.auth import auth_bp
from routes.quiz import quiz_bp

load_dotenv("key.env")

app = Flask(__name__)

# Configure CORS to allow credentials from frontend for all routes
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    }
})

app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/test')
def test_clerk():
    with Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY")) as sdk:
        try:
            response = sdk.users.list()
            
            nb_users = len(response)
            
            return f"Connexion OK  {nb_users}"
        
        except Exception as e:
            return f"Erreur de connexion : {str(e)}"

@app.route('/check-mongodb')
def check_mongodb():
    """Check MongoDB connection status"""
    success, message = check_mongodb_connection()
    if success:
        return jsonify({"connected": True, "message": message}), 200
    else:
        return jsonify({"connected": False, "error": message}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


