
import os
import uuid
from flask import Blueprint, request, jsonify
from models.quiz_models import BattleModel, BattleStatus
from services.clerk_auth import ClerkAuthService
from datetime import datetime
from config.db import mongodb_connection
from pymongo.errors import PyMongoError
from models.user import UserBase, UserUpdate

import os
import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security import authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions
quiz_bp = Blueprint('quiz', __name__)
db = mongodb_connection().get_database("hackathon_db")
def get_all_quizzes():
    quizzes = list(db.quizzes.find({}, {"_id": 1, "title": 1, "category": 1}))
    for q in quizzes: q['_id'] = str(q['_id'])
    return jsonify(quizzes), 200
@quiz_bp.route('/quizzes/<quiz_id>', methods=['GET'])
def get_quiz_by_id(quiz_id):
    quiz_data = db.quizzes.find_one({"id": quiz_id}, {"_id": 0})
    if not quiz_data:
        return jsonify({"success": False, "error": "Quiz introuvable"}), 404
    
    for q in quiz_data['questions']:
        del q['correct_answer']
        
    return jsonify({"success": True, "quiz": quiz_data}), 200

@quiz_bp.route('/quizzes/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    clerk_id = data.get('clerk_id')
    quiz_id = data.get('quiz_id')
    user_answers = data.get('answers') 
    original_quiz = db.quizzes.find_one({"id": quiz_id})
    if not original_quiz:
        return jsonify({"success": False, "error": "Quiz non trouvé"}), 404
    total_score = 0
    detailed_answers = []
    for user_ans in user_answers:
        question = next((q for q in original_quiz['questions'] if q['id'] == user_ans['question_id']), None)
        
        if question:
            is_correct = (user_ans['selected_option'] == question['correct_answer'])
            if is_correct:
                total_score += question['points']
            
            detailed_answers.append({
                "question_id": question['id'],
                "selected_option": user_ans['selected_option'],
                "is_correct": is_correct
            })
    result_data = {
        "clerk_id": clerk_id,
        "quiz_id": quiz_id,
        "score": total_score,
        "answers": detailed_answers
    }
    db.results.insert_one(result_data)

    return jsonify({"success": True, "score": total_score, "details": detailed_answers}), 200
