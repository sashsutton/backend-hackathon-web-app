# Backend for AMU Hackathon 2026 Quiz App

## Overview
This backend supports a quiz application designed to strengthen cohesion among computer science students at Aix-Marseille University. The app facilitates quiz-based interactions between undergraduate and graduate students.

**Frontend Repository**: [frontend-hackathon-quizz-app](https://github.com/sashsutton/frontend-hackathon-quizz-app)

## Features
- User authentication via Clerk
- Quiz creation and management
- Duel mode for competitive quizzing
- Session-based interactions

## Setup

### Prerequisites
- Python 3.12+
- Flask
- Clerk API key

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend-hackathon-web-app-2
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Set environment variables:
   ```bash
   export CLERK_SECRET_KEY=your_clerk_secret_key
   export DATABASE_URL=your_database_url
   ```

6. Run the application:
   ```bash
   flask run
   ```

## API Endpoints
- `/auth`: Authentication routes
- `/quiz`: Quiz management
- `/duel`: Duel mode

## Project Structure
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

## License
MIT
