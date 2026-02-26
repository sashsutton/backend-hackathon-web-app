
import httpx
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.quiz_model import QuizResult, UserAnswerModel, QuestionModel, QuizModel
from services.quiz_service import QuizService
from config.db import mongodb_connection
from middleware.clerk_auth import clerk_auth_middleware, get_current_user
import csv
import io
quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quiz/get-all-quizzes', methods=['GET'])
@clerk_auth_middleware
def get_all_quizzes():
    mongo_client = mongodb_connection()
    db = mongo_client.get_database("hackathon_db")
    quiz_service = QuizService(db)

    quizzes = quiz_service.get_all_quizzes()
    return jsonify(quizzes), 200


@quiz_bp.route('/quiz/page/<quiz_id>', methods=['GET'])
@clerk_auth_middleware
def get_page_quiz_by_id(quiz_id):
    from bson import ObjectId

    mongo_client = mongodb_connection()
    db = mongo_client.get_database("hackathon_db")

    try:
        # Try to find by MongoDB ObjectId first (sent from frontend as quiz._id)
        quiz_data = None
        try:
            quiz_data = db.quizzes.find_one({"_id": ObjectId(quiz_id)})
        except Exception:
            pass

        # Fallback: try by custom string id field
        if not quiz_data:
            quiz_data = db.quizzes.find_one({"id": quiz_id})

        if not quiz_data:
            return jsonify({"success": False, "message": "Quiz not found"}), 404

        quiz_data['_id'] = str(quiz_data['_id'])

        return jsonify({"success": True, "quiz": quiz_data}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@quiz_bp.route('/quiz/<quiz_id>', methods=['GET'])
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

@quiz_bp.route('/quiz/create-question', methods=['POST'])
@clerk_auth_middleware
def create_question():
    try:
        data = request.get_json()
        print(f"Requête reçue pour créer une question : {data}")  # Log pour déboguer
        
        mongo_client = mongodb_connection()
        db = mongo_client.get_database("hackathon_db")
        quiz_service = QuizService(db)

        question_id = quiz_service.create_question(data)
        print(f"Question créée avec succès. ID : {question_id}")  # Log pour déboguer
        
        return jsonify({
            "success": True,
            "question_id": question_id,
            "message": "Question created successfully"
        }), 201
        
    except ValidationError as e:
        print(f"Erreur de validation : {e.errors()}")  # Log pour déboguer
        return jsonify({
            "success": False,
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        print(f"Erreur lors de la création de la question : {str(e)}")  # Log pour déboguer
        return jsonify({
            "success": False,
            "error": f"Failed to create question: {str(e)}"
        }), 500

@quiz_bp.route('/quiz/get-all-questions', methods=['GET'])
@clerk_auth_middleware
def get_all_questions():
    try:
        mongo_client = mongodb_connection()
        db = mongo_client.get_database("hackathon_db")
        quiz_service = QuizService(db)

        questions = quiz_service.get_all_questions()
        
        return jsonify({
            "success": True,
            "questions": questions,
            "count": len(questions)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve questions: {str(e)}"
        }), 500

@quiz_bp.route('/quiz/get-question/<int:question_id>', methods=['GET'])
@clerk_auth_middleware
def get_question_by_id(question_id):
    try:
        mongo_client = mongodb_connection()
        db = mongo_client.get_database("hackathon_db")
        quiz_service = QuizService(db)

        question = quiz_service.get_question_by_id(question_id)
        
        return jsonify({
            "success": True,
            "question": question
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve question: {str(e)}"
        }), 500

@quiz_bp.route('/quiz/create-quiz', methods=['POST'])
@clerk_auth_middleware
def create_quiz():
    try:
        data = request.get_json()

        if 'questions' in data:

            mongo_client = mongodb_connection()
            db = mongo_client.get_database("hackathon_db")
            quiz_service = QuizService(db)
            

            quiz_id = quiz_service.create_quiz(data)
            
            return jsonify({
                "success": True,
                "quiz_id": quiz_id,
                "message": "Quiz created successfully"
            }), 201
        elif 'question_ids' in data:
            # Cas pour créer un quiz depuis des IDs de questions existants
            mongo_client = mongodb_connection()
            db = mongo_client.get_database("hackathon_db")
            quiz_service = QuizService(db)

            # Récupérer les questions complètes depuis MongoDB (avec correct_answer)
            questions = []
            for question_id in data['question_ids']:
                from bson import ObjectId
                q = db.questions.find_one({"_id": ObjectId(question_id)})
                if q:
                    q.pop("_id", None)
                    # S'assurer que tous les champs requis par QuestionModel sont présents
                    questions.append(q)

            # Créer un objet quiz complet avec le bon mapping de champs
            quiz_data = {
                'title': data.get('title'),
                'category': data.get('description', ''),   # description → category
                'difficulty': data.get('level', 'medium'), # level → difficulty
                'questions': questions
            }

            quiz_id = quiz_service.create_quiz(quiz_data)

            return jsonify({
                "success": True,
                "quiz_id": quiz_id,
                "message": "Quiz created successfully from question IDs"
            }), 201
        else:

            user_answers = [UserAnswerModel(**answer) for answer in data.get('answers', [])]
            
            quiz_result_data = {
                'clerk_id': data.get('clerk_id'),
                'quiz_id': data.get('quiz_id'),
                'score': 0,
                'answers': user_answers
            }
            quiz_result = QuizResult(**quiz_result_data)
            
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
            
    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to process quiz: {str(e)}"
        }), 500
