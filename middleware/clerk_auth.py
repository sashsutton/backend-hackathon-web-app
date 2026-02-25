import os
import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv("key.env")

def clerk_auth_middleware(f):
    """
    Flask middleware for Clerk authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:

            httpx_request = httpx.Request(
                method=request.method,
                url=request.url,
                headers=dict(request.headers),
                cookies=request.cookies,
                content=request.get_data()
            )


            secret_key = os.getenv("CLERK_SECRET_KEY")
            if not secret_key:
                return jsonify({"error": "Server configuration error"}), 500

            sdk = Clerk(bearer_auth=secret_key)
            

            request_state = sdk.authenticate_request(
                httpx_request,
                AuthenticateRequestOptions(
                    authorized_parties=[os.getenv("FRONTEND_URL", "http://localhost:3000")]
                )
            )


            if not request_state.is_signed_in:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "reason": request_state.reason
                }), 401


            request.clerk_user = request_state.payload
            request.clerk_request_state = request_state

            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }), 500
    
    return decorated_function

def get_current_user():
    """
    Helper function to get current user from request.
    """
    if not hasattr(request, 'clerk_user'):
        return None
    return request.clerk_user