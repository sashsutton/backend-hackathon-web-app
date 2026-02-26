

import os
from flask import Blueprint, request, jsonify
from services.clerk_auth import ClerkAuthService
from datetime import datetime
from config.db import mongodb_connection
from pymongo.errors import PyMongoError
from models.user import UserBase, UserUpdate
import httpx

auth_bp = Blueprint('auth', __name__)

clerk_auth_service = ClerkAuthService()

def store_user_in_database(clerk_id: str, email: str, first_name: str = "", last_name: str = "", promotion: str = "licence", mention: str = "informatique") -> bool:

    try:
        client = mongodb_connection()
        db = client.get_database("hackathon_db")
        users_collection = db["users"]

        name = f"{first_name} {last_name}".strip()

            
        user_data = {
            "clerk_id": clerk_id,
            "name": name,
            "email": email,
            "promotion": promotion,
            "mention": mention,
            "created_at": datetime.utcnow()
        }

        result = users_collection.insert_one(user_data)
        return result.inserted_id is not None
        
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        print(f"MongoDB URI: {os.getenv('MONGODB_URI', 'Not set')}")
        return False
    except Exception as e:
        print(f"Unexpected error storing user: {str(e)}")
        print(f"MongoDB URI: {os.getenv('MONGODB_URI', 'Not set')}")
        return False

@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        

        #  On utilise la fonction create_user (clerk_auth.py dans services) pour crée un utilisateur sur clerk
        success, result = clerk_auth_service.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        
        if not success:
            return jsonify({
                "success": False,
                "error": result
            }), 400
        

        clerk_id = result.get('user_id')
        email = result.get('email')
        first_name = result.get('first_name', '')
        last_name = result.get('last_name', '')


        promotion = data.get('promotion', 'licence')
        mention = data.get('mention', 'informatique')

        UserBase(clerk_id=clerk_id, email=email, first_name=first_name, last_name=last_name, promotion=promotion, mention=mention)


        #On utilise la fonction qui nous permet de sauvegarder l'utilisateur dans la base de donnée
        db_success = store_user_in_database(
            clerk_id=clerk_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            promotion=promotion,
            mention=mention
        )
        
        if not db_success:
            print(f"Warning: Failed to store user {clerk_id} in database")

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": result,
            "database_stored": db_success
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Registration failed: {str(e)}"
        }), 500
<<<<<<< HEAD
        
        
=======
>>>>>>> d15abcb3ad0fff9dc217463381d8ce3be5a76272

@auth_bp.route('/auth/me', methods=['GET'])
def get_my_info():
    """
    Get current authenticated user information.
    Uses Clerk's authenticate_request to verify the session.
    """
    try:
<<<<<<< HEAD
        
        clerk_req = httpx.Request(
=======
        # Convert Flask request to httpx.Request for Clerk authentication
        my_clerk_request = httpx.Request(
>>>>>>> d15abcb3ad0fff9dc217463381d8ce3be5a76272
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            content=request.get_data()
        )

<<<<<<< HEAD
        state = clerk_auth_service.verify_clerk_session(clerk_req)

        if not state.is_signed_in:
            return jsonify({
                "success": False, 
                "error": "Non connecté", 
                "reason": str(state.reason)
            }), 401

        user_info = state.payload 

        return jsonify({
            "success": True,
            "message": "Infos récupérées du Payload",
            "user_id": user_info.get("sub"), 
            "details_du_front": user_info
=======
        # Authenticate the request using Clerk's backend SDK
        request_state = clerk_auth_service.is_signed_in(my_clerk_request)

        # Check if user is signed in
        if not request_state.is_signed_in:
            return jsonify({
                "success": False,
                "error": "Invalid session",
                "reason": request_state.reason
            }), 401

        # Return user information from the authenticated payload
        return jsonify({
            "success": True,
            "clerk_id": request_state.payload.get("sub"),
            "email": request_state.payload.get("email", ""),
            "first_name": request_state.payload.get("first_name", ""),
            "last_name": request_state.payload.get("last_name", ""),
            "full_payload": request_state.payload
>>>>>>> d15abcb3ad0fff9dc217463381d8ce3be5a76272
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Authentication check failed: {str(e)}"
        }), 500
@auth_bp.route('/auth/login', methods=['POST'])
def login():

    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                "success": False,
                "error": "Email and password are required"
            }), 400

        success, result = clerk_auth_service.authenticate_user(
            data['email'],
            data['password']
        )
        
        if not success:
            return jsonify({
                "success": False,
                "error": result
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Login failed: {str(e)}"
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():

    try:
        return jsonify({
            "success": True,
            "message": "Logout successful"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Logout failed: {str(e)}"
        }), 500
