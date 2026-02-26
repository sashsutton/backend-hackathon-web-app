import os
import httpx
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from config.db import mongodb_connection

load_dotenv("key.env")

clerk_secret_key = os.getenv('CLERK_SECRET_KEY')

if not clerk_secret_key:
    raise ValueError("CLERK_SECRET_KEY environment variable is not set")

clerk_client = Clerk(bearer_auth=clerk_secret_key)


def clerk_auth_middleware(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        httpx_req = httpx.Request(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            cookies=request.cookies,
            content=request.get_data()
        )

        try:
            request_state = clerk_client.authenticate_request(
                httpx_req,
                AuthenticateRequestOptions(
                    authorized_parties=[os.getenv("FRONTEND_URL", "http://localhost:3000")]
                )
            )

            if not request_state.is_signed_in:
                return jsonify({"error": "Unauthorized", "reason": request_state.reason}), 401


            clerk_user_id = request_state.payload.get("sub")

            if not clerk_user_id:
                return jsonify({"error": "Invalid token payload"}), 401

            mongo_client = mongodb_connection()
            user = mongo_client.users.find_one({"clerk_id": clerk_user_id})

            if not user:
                print(f"New user detected! Fetching details for {clerk_user_id}")

                try:
                    clerk_user_profile = clerk_client.users.get(user_id=clerk_user_id)
                    first_name = clerk_user_profile.first_name or ""
                    last_name = clerk_user_profile.last_name or ""

                    email = ""
                    if clerk_user_profile.email_addresses:
                        email = clerk_user_profile.email_addresses[0].email_address

                except Exception as e:
                    print(f"Failed to fetch user profile from Clerk: {e}")
                    first_name = "Unknown"
                    last_name = ""
                    email = ""

                user = {
                    "clerk_id": clerk_user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "elo_rating": 1200,
                    "total_duels": 0,
                    "wins": 0,
                    "losses": 0
                }


                mongo_client.users.insert_one(user)
                print(f"Successfully created DB profile for {first_name} {last_name}")


            request.clerk_user = user

        except Exception as e:
            print(f"Unexpected Auth error: {e}")
            return jsonify({"error": "Authentication processing failed"}), 500

        return f(*args, **kwargs)

    return decorated

def get_current_user():
    """
    Helper function to get current user from request.
    """
    if not hasattr(request, 'clerk_user'):
        return None
    return request.clerk_user
