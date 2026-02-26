import os
from flask import Blueprint, request, jsonify
from services.clerk_auth import ClerkAuthService
from middleware.clerk_auth import clerk_auth_middleware
from models.user_model import UserBase, UserUpdate
from config.db import mongodb_connection

auth_bp = Blueprint('auth', __name__)

clerk_auth_service = ClerkAuthService()


@auth_bp.route('/auth/me', methods=['GET'])
@clerk_auth_middleware
def get_my_info():
    """
    Get current authenticated user information from MongoDB.
    The middleware validates the Clerk session and populates request.clerk_user_id.
    MongoDB is the source of truth — it already holds first_name, last_name, email
    (synced from Clerk on first login) plus all game-specific fields.
    """
    try:
        clerk_id = request.clerk_user_id
        db = mongodb_connection().get_database("hackathon_db")
        user = db["users"].find_one({"clerk_id": clerk_id})

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found in database"
            }), 404

        return jsonify({
            "success": True,
            "clerk_id": user.get("clerk_id"),
            "email": user.get("email", ""),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "promotion": user.get("promotion", ""),
            "mention": user.get("mention", ""),
            "elo": user.get("elo", 1200),
            "wins": user.get("wins", 0),
            "losses": user.get("losses", 0),
            "total_duels": user.get("total_duels", 0)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get user information: {str(e)}"
        }), 500


@auth_bp.route('/auth/profile', methods=['PUT'])
@clerk_auth_middleware
def update_profile():
    """
    Update current authenticated user's profile information.
    Uses Clerk middleware to verify the session.
    """
    try:
        # Get the current user from the middleware
        current_user = request.clerk_user


        update_data = request.get_json()

        update_fields = {}
        allowed = ['first_name', 'last_name', 'promotion', 'mention', 'email']
        for field in allowed:
            if field in update_data and update_data[field]:
                update_fields[field] = update_data[field]

        if not update_fields:
            return jsonify({"success": False, "error": "No valid fields to update"}), 400

        # Update the user in MongoDB
        db = mongodb_connection().get_database("hackathon_db")
        current_user = request.clerk_user
        result = db["users"].update_one(
            {"clerk_id": current_user.get("clerk_id")},
            {"$set": update_fields}
        )

        updated_user = db["users"].find_one({"clerk_id": current_user.get("clerk_id")})


        return jsonify({
            "success": True,
            "user": {
                "clerk_id": updated_user.get("clerk_id"),
                "email": updated_user.get("email", ""),
                "first_name": updated_user.get("first_name", ""),
                "last_name": updated_user.get("last_name", ""),
                "promotion": updated_user.get("promotion", ""),
                "mention": updated_user.get("mention", ""),
                "elo": updated_user.get("elo", 1200),
                "wins": updated_user.get("wins", 0),
                "losses": updated_user.get("losses", 0),
                "total_duels": updated_user.get("total_duels", 0)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update profile: {str(e)}"
        }), 500


@auth_bp.route('/leaderboard', methods=['GET'])
@clerk_auth_middleware
def get_leaderboard():
    try:
        db = mongodb_connection().get_database("hackathon_db")
        users = list(db["users"].find({}, {
            "_id": 0,
            "clerk_id": 1,
            "first_name": 1,
            "last_name": 1,
            "promotion": 1,
            "mention": 1,
            "elo": 1,
            "wins": 1,
            "losses": 1,
            "total_duels": 1
        }).sort("elo", -1).limit(50))

        return jsonify({"success": True, "leaderboard": users}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500