import os
from clerk_backend_api import Clerk
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from config.db import mongodb_connection, check_mongodb_connection
from services.clerk_auth import ClerkAuthService

load_dotenv("key.env")

app = Flask(__name__)

# Initialize services
clerk_auth_service = ClerkAuthService()

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

@app.route('/health-check')
def health_check():
    success, message = check_mongodb_connection()
    if success:
        return jsonify({"status": "healthy", "message": message}), 200
    else:
        return jsonify({"status": "unhealthy", "error": message}), 500

@app.route('/check-mongodb')
def check_mongodb():
    """Check MongoDB connection status"""
    success, message = check_mongodb_connection()
    if success:
        return jsonify({"connected": True, "message": message}), 200
    else:
        return jsonify({"connected": False, "error": message}), 500

if __name__ == '__main__':
    app.run(debug=True)


