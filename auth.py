import os

from pydantic import ValidationError
from clerk_backend_api import Clerk
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from config.db import mongodb_connection, check_mongodb_connection
from models.user import UserUpdate
from services.clerk_auth import ClerkAuthService
from flask import Blueprint, jsonify, current_app
load_dotenv("key.env")
db = mongodb_connection()
users_collection = db['users']
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login',methods=['POST'])
def login():
    data= request.json
    email=data.get('email')
    user = users_collection.find_one({"email": email}, {"_id": 0})
    if user:
        return jsonify({"status": "Authenticated", "user": user}), 200
    return jsonify({"error": "User not found in local DB"}), 404
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = UserUpdate(**request.json)
        
        with Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY")) as sdk:
            clerk_user = sdk.users.create(
                email_address=[data.email],
                password=data.password,
                first_name=data.name
            )
            
            user_doc = data.model_dump(exclude={'password'}) 
            user_doc['clerk_id'] = clerk_user.id
            
            users_collection.insert_one(user_doc)
            
            return jsonify({"message": "Utilisateur créé !", "user": user_doc}), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500