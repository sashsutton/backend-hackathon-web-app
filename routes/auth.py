

from flask import Blueprint, request, jsonify
from services.clerk_auth import ClerkAuthService
from models import UserCreate, UserResponse
from datetime import datetime
from config.db import mongodb_connection
from pymongo.errors import PyMongoError


auth_bp = Blueprint('auth', __name__)

clerk_auth_service = ClerkAuthService()

def store_user_in_database(clerk_id: str, email: str, first_name: str = "", last_name: str = "", promotion: str = "licence", mention: str = "informatique") -> bool:

    try:
        client = mongodb_connection()
        db = client.get_database("hackathon_db")
        users_collection = db["users"]

        name = f"{first_name} {last_name}".strip()
        if not name:
            name = email.split('@')[0]
            
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
        return False
    except Exception as e:
        print(f"Unexpected error storing user: {str(e)}")
        return False

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        
        # Create user in Clerk
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

@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():

    try:

        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required"
            }), 400

        success, result = clerk_auth_service.get_user_by_id(user_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": result
            }), 404
        
        return jsonify({
            "success": True,
            "user": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get user: {str(e)}"
        }), 500

@auth_bp.route('/auth/users', methods=['GET'])
def list_users():

    try:

        success, result = clerk_auth_service.list_all_users()

        if not success:
            return jsonify({
                "success": False,
                "error": result
            }), 500

        return jsonify({
            "success": True,
            "users": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list users: {str(e)}"
        }), 500