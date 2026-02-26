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


        from models.user_model import UserUpdate
        validated_update = UserUpdate(**update_data)


        update_fields = {}
        if validated_update.name:
            # Split name into first and last name
            name_parts = validated_update.name.split(' ', 1)
            update_fields['first_name'] = name_parts[0]
            if len(name_parts) > 1:
                update_fields['last_name'] = name_parts[1]
        if validated_update.promotion:
            update_fields['promotion'] = validated_update.promotion
        if validated_update.mention:
            update_fields['mention'] = validated_update.mention
        if validated_update.email:
            update_fields['email'] = validated_update.email

        # Update the user in MongoDB
        db = mongodb_connection().get_database("hackathon_db")
        result = db["users"].update_one(
            {"clerk_id": current_user.get("clerk_id")},
            {"$set": update_fields}
        )

        if result.modified_count == 0:
            return jsonify({
                "success": False,
                "error": "No changes made or user not found"
            }), 404


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