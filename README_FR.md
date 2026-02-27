# Backend pour l'Application Quiz du Hackathon AMU 2026

## Aperçu
Ce backend supporte une application de quiz conçue pour renforcer la cohésion entre les étudiants en licence et master d'informatique à l'Université d'Aix-Marseille. L'application facilite les interactions basées sur des quiz entre les étudiants de premier et deuxième cycle.

## Fonctionnalités
- Authentification des utilisateurs via Clerk
- Création et gestion de quiz
- Mode duel pour des quiz compétitifs
- Interactions basées sur des sessions

## Configuration

### Prérequis
- Python 3.12+
- Flask
- Clé API Clerk

### Installation
1. Clonez le dépôt :
   ```bash
   git clone <repository-url>
   cd backend-hackathon-web-app-2
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez la base de données :
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Définissez les variables d'environnement :
   ```bash
   export CLERK_SECRET_KEY=votre_clé_secrète_clerk
   export DATABASE_URL=votre_url_de_base_de_données
   ```

6. Exécutez l'application :
   ```bash
   flask run
   ```

## Points de Terminaison de l'API
- `/auth` : Routes d'authentification
- `/quiz` : Gestion des quiz
- `/duel` : Mode duel

## Structure du Projet
```
backend-hackathon-web-app-2/
├── config/
│   └── db.py
├── middleware/
│   └── clerk_auth.py
├── models/
│   ├── quiz_model.py
│   └── user_model.py
├── routes/
│   ├── auth.py
│   ├── duel.py
│   └── quiz.py
├── services/
│   ├── clerk_auth.py
│   └── quiz_service.py
└── app.py
```

## Licence
MIT
