
import httpx
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.quiz_models import QuizResult, UserAnswerModel
from services.quiz_service import QuizService
from config.db import mongodb_connection
from middleware.clerk_auth import clerk_auth_middleware, get_current_user
quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz/get-all-quizzes', methods=['GET'])
@clerk_auth_middleware
def get_all_quizzes():
    mongo_client = mongodb_connection()
    db = mongo_client.get_database("hackathon_db")
    quiz_service = QuizService(db)
    quizzes = quiz_service.get_all_quizzes()
    return jsonify(quizzes), 200
@quiz_bp.route('/quizzes/<quiz_id>', methods=['GET'])
@clerk_auth_middleware
def get_quiz_by_id(quiz_id):
    mongo_client = mongodb_connection()
    db = mongo_client.get_database("hackathon_db")
    try:
        quiz_service = QuizService(db)
        quiz_data = quiz_service.get_quiz_by_id(quiz_id)
        return jsonify({"success": True, "quiz": quiz_data}), 200
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Une erreur est survenue"}), 500

@quiz_bp.route('/quiz/create-quiz', methods=['POST'])
@clerk_auth_middleware
def create_quiz():
    try:
        data = request.get_json()
        

        user_answers = [UserAnswerModel(**answer) for answer in data.get('answers', [])]
        

        quiz_result_data = {
            'clerk_id': data.get('clerk_id'),
            'quiz_id': data.get('quiz_id'),
            'score': 0,
            'answers': user_answers
        }
        quiz_result = QuizResult(**quiz_result_data)
        
    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Missing required field: {str(e)}"
        }), 400

    mongo_client = mongodb_connection()
    db = mongo_client.get_database("hackathon_db")


    current_user = get_current_user()
    if current_user:
        clerk_id = current_user.get('id') or quiz_result.clerk_id
    else:
        clerk_id = quiz_result.clerk_id
    quiz_id = quiz_result.quiz_id
    user_answers = quiz_result.answers
    

    quiz_service = QuizService(db)
    

    quiz_result_with_score = quiz_service.calculate_quiz_score(quiz_id, user_answers)
    quiz_result_with_score.clerk_id = clerk_id
    

    result_id = quiz_service.save_quiz_result(quiz_result_with_score)

    return jsonify({
        "success": True, 
        "score": quiz_result_with_score.score, 
        "details": quiz_result_with_score.answers,
        "result_id": result_id
    }), 200
