
import os
from clerk_backend_api import Clerk
from dotenv import load_dotenv

load_dotenv("key.env")

class ClerkAuthService:

    
    def __init__(self):
        self.secret_key = os.getenv("CLERK_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("CLERK_SECRET_KEY environment variable not set")
    
    def get_clerk_client(self):
        return Clerk(bearer_auth=self.secret_key)
    
    def authenticate_user(self, email: str, password: str) -> tuple:
        try:
            with Clerk(bearer_auth=self.secret_key) as sdk:

                users = sdk.users.list()

                target_user = None
                for user in users:
                    if hasattr(user, 'email_addresses') and user.email_addresses:
                        for email_addr in user.email_addresses:
                            if email_addr.email_address == email:
                                target_user = user
                                break
                    if target_user:
                        break
                
                if not target_user:
                    return False, "User not found"
                

                return True, {
                    "user_id": target_user.id,
                    "email": email,
                    "first_name": getattr(target_user, 'first_name', ''),
                    "last_name": getattr(target_user, 'last_name', '')
                }
                
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"
    
    def get_user_by_id(self, user_id: str) -> tuple:

        try:
            with Clerk(bearer_auth=self.secret_key)  as sdk:
                user = sdk.users.get(user_id)
                return True, {
                    "user_id": user.id,
                    "email_addresses": [ea.email_address for ea in user.email_addresses],
                    "first_name": getattr(user, 'first_name', ''),
                    "last_name": getattr(user, 'last_name', ''),
                    "created_at": getattr(user, 'created_at', None)
                }
        except Exception as e:
            return False, f"Failed to get user: {str(e)}"
    
    def list_all_users(self) -> tuple:

        try:
            with Clerk(bearer_auth=self.secret_key) as sdk:
                users = sdk.users.list()
                user_list = []
                for user in users:
                    user_list.append({
                        "user_id": user.id,
                        "email_addresses": [ea.email_address for ea in user.email_addresses],
                        "first_name": getattr(user, 'first_name', ''),
                        "last_name": getattr(user, 'last_name', ''),
                        "created_at": getattr(user, 'created_at', None)
                    })
                return True, user_list
        except Exception as e:
            return False, f"Failed to list users: {str(e)}"
    
    def create_user(self, email: str, password: str, first_name: str = "", last_name: str = "") -> tuple:

        try:
            with Clerk(bearer_auth=self.secret_key) as sdk:
                new_user = sdk.users.create(
                    email_address=[email],
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                return True, {
                    "user_id": new_user.id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
        except Exception as e:
            return False, f"Failed to create user: {str(e)}"

