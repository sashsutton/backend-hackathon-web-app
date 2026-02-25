import os
from clerk_backend_api import Clerk
from dotenv import load_dotenv
from flask import Flask

load_dotenv("key.env") # <--- Correction ici

app = Flask(__name__)

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

@app.route('/create-test')
def create_user():
    with Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY")) as sdk:
        try:
            new_user = sdk.users.create(
                email_address=["test-user@example.com"], 
                password="MotDePasseTresSecurise123!",
                first_name="fadila",
                last_name="zaiba"
            )
            
            return f"<h1>Succès !</h1>Utilisateur créé avec l'ID : <b>{new_user.id}</b>"
        
        except Exception as e:
            return f"<h1>Erreur</h1> {str(e)}"
if __name__ == '__main__':
    app.run(debug=True)