import random
import string
from flask import Blueprint, request, jsonify
from middleware.clerk_auth import clerk_auth_middleware, get_current_user
from config.db import mongodb_connection
from bson import ObjectId
from datetime import datetime

duel_bp = Blueprint('duel', __name__)

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_db():
    return mongodb_connection().get_database("hackathon_db")

def serialize_duel(duel):
    duel['_id'] = str(duel['_id'])
    return duel

# ─── Create duel ────────────────────────────────────────────────────────────

@duel_bp.route('/duel/create', methods=['POST'])
@clerk_auth_middleware
def create_duel():
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        if not quiz_id:
            return jsonify({"success": False, "error": "quiz_id is required"}), 400

        current_user = get_current_user()
        clerk_id = current_user.get('clerk_id')

        db = get_db()

        # Verify quiz exists
        try:
            quiz = db.quizzes.find_one({"_id": ObjectId(quiz_id)})
        except Exception:
            quiz = None
        if not quiz:
            return jsonify({"success": False, "error": "Quiz not found"}), 404

        room_code = generate_room_code()
        # Ensure unique code
        while db.duels.find_one({"room_code": room_code, "status": "waiting"}):
            room_code = generate_room_code()

        duel_doc = {
            "room_code": room_code,
            "quiz_id": quiz_id,
            "player1_id": clerk_id,
            "player2_id": None,
            "status": "waiting",
            "player1_score": 0,
            "player2_score": 0,
            "player1_done": False,
            "player2_done": False,
            "winner_id": None,
            "created_at": datetime.utcnow()
        }

        result = db.duels.insert_one(duel_doc)
        duel_id = str(result.inserted_id)

        return jsonify({
            "success": True,
            "duel_id": duel_id,
            "room_code": room_code
        }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── Join duel ───────────────────────────────────────────────────────────────

@duel_bp.route('/duel/join/<room_code>', methods=['POST'])
@clerk_auth_middleware
def join_duel(room_code):
    try:
        current_user = get_current_user()
        clerk_id = current_user.get('clerk_id')

        db = get_db()
        duel = db.duels.find_one({"room_code": room_code.upper(), "status": "waiting"})

        if not duel:
            return jsonify({"success": False, "error": "Duel introuvable ou déjà commencé"}), 404

        if duel['player1_id'] == clerk_id:
            return jsonify({"success": False, "error": "Vous ne pouvez pas rejoindre votre propre duel"}), 400

        duel_id = str(duel['_id'])

        db.duels.update_one(
            {"_id": duel['_id']},
            {"$set": {"player2_id": clerk_id, "status": "in_battle"}}
        )

        # Notify Player 1's socket via server-side emit — no client socket needed
        from extensions import socketio
        socketio.emit('duel:started', {"duel_id": duel_id}, to=duel_id)

        return jsonify({
            "success": True,
            "duel_id": duel_id,
            "quiz_id": duel['quiz_id']
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── Get duel status ─────────────────────────────────────────────────────────

@duel_bp.route('/duel/<duel_id>', methods=['GET'])
@clerk_auth_middleware
def get_duel(duel_id):
    try:
        db = get_db()
        duel = db.duels.find_one({"_id": ObjectId(duel_id)})
        if not duel:
            return jsonify({"success": False, "error": "Duel not found"}), 404

        # Get player names
        def get_name(clerk_id):
            if not clerk_id:
                return None
            user = db.users.find_one({"clerk_id": clerk_id})
            if user:
                return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            return clerk_id

        return jsonify({
            "success": True,
            "duel": {
                "_id": str(duel['_id']),
                "room_code": duel.get('room_code'),
                "quiz_id": duel.get('quiz_id'),
                "status": duel.get('status'),
                "player1_id": duel.get('player1_id'),
                "player2_id": duel.get('player2_id'),
                "player1_name": get_name(duel.get('player1_id')),
                "player2_name": get_name(duel.get('player2_id')),
                "player1_score": duel.get('player1_score', 0),
                "player2_score": duel.get('player2_score', 0),
                "player1_done": duel.get('player1_done', False),
                "player2_done": duel.get('player2_done', False),
                "winner_id": duel.get('winner_id'),
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── Submit duel answers ─────────────────────────────────────────────────────

@duel_bp.route('/duel/<duel_id>/submit', methods=['POST'])
@clerk_auth_middleware
def submit_duel(duel_id):
    try:
        data = request.get_json()
        answers = data.get('answers', [])

        current_user = get_current_user()
        clerk_id = current_user.get('clerk_id')

        db = get_db()
        duel = db.duels.find_one({"_id": ObjectId(duel_id)})
        if not duel:
            return jsonify({"success": False, "error": "Duel not found"}), 404

        is_player1 = (duel['player1_id'] == clerk_id)
        is_player2 = (duel.get('player2_id') == clerk_id)

        if not is_player1 and not is_player2:
            return jsonify({"success": False, "error": "You are not part of this duel"}), 403

        # Calculate score
        quiz = db.quizzes.find_one({"_id": ObjectId(duel['quiz_id'])})
        if not quiz:
            return jsonify({"success": False, "error": "Quiz not found"}), 404

        questions = quiz.get('questions', [])
        total_score = 0
        for ans in answers:
            q_id = str(ans.get('question_id'))
            selected = str(ans.get('selected_option', ''))
            for idx, q in enumerate(questions):
                db_q_id = str(q.get('id')) if q.get('id') is not None else str(idx)
                if db_q_id == q_id:
                    if selected == str(q.get('correct_answer', '')):
                        total_score += int(q.get('points', 10))
                    break

        # Update the duel
        score_field = 'player1_score' if is_player1 else 'player2_score'
        done_field = 'player1_done' if is_player1 else 'player2_done'

        update = {"$set": {score_field: total_score, done_field: True}}
        db.duels.update_one({"_id": ObjectId(duel_id)}, update)

        # Refresh duel
        duel = db.duels.find_one({"_id": ObjectId(duel_id)})
        both_done = duel.get('player1_done') and duel.get('player2_done')

        winner_id = None
        elo_change = 0

        if both_done:
            p1_score = duel.get('player1_score', 0)
            p2_score = duel.get('player2_score', 0)

            if p1_score > p2_score:
                winner_id = duel['player1_id']
            elif p2_score > p1_score:
                winner_id = duel.get('player2_id')
            # else: draw — no winner

            db.duels.update_one(
                {"_id": ObjectId(duel_id)},
                {"$set": {"status": "finished", "winner_id": winner_id}}
            )

            # Update ELO and stats
            ELO_CHANGE = 20
            p1_id = duel['player1_id']
            p2_id = duel.get('player2_id')

            if p2_id:
                if winner_id == p1_id:
                    db.users.update_one({"clerk_id": p1_id}, {"$inc": {"elo": ELO_CHANGE, "wins": 1, "total_duels": 1}})
                    db.users.update_one({"clerk_id": p2_id}, {"$inc": {"elo": -ELO_CHANGE, "losses": 1, "total_duels": 1}})
                elif winner_id == p2_id:
                    db.users.update_one({"clerk_id": p2_id}, {"$inc": {"elo": ELO_CHANGE, "wins": 1, "total_duels": 1}})
                    db.users.update_one({"clerk_id": p1_id}, {"$inc": {"elo": -ELO_CHANGE, "losses": 1, "total_duels": 1}})
                else:
                    # Draw
                    db.users.update_one({"clerk_id": p1_id}, {"$inc": {"total_duels": 1}})
                    db.users.update_one({"clerk_id": p2_id}, {"$inc": {"total_duels": 1}})

            if winner_id == clerk_id:
                elo_change = ELO_CHANGE
            elif winner_id and winner_id != clerk_id:
                elo_change = -ELO_CHANGE

        return jsonify({
            "success": True,
            "score": total_score,
            "both_done": both_done,
            "winner_id": winner_id,
            "elo_change": elo_change,
            "player1_score": duel.get('player1_score', 0) if is_player1 else None,
            "player2_score": duel.get('player2_score', 0) if is_player2 else None,
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── My duels history ────────────────────────────────────────────────────────

@duel_bp.route('/duel/my-duels', methods=['GET'])
@clerk_auth_middleware
def my_duels():
    try:
        current_user = get_current_user()
        clerk_id = current_user.get('clerk_id')
        db = get_db()

        duels = list(db.duels.find({
            "$or": [{"player1_id": clerk_id}, {"player2_id": clerk_id}]
        }).sort("created_at", -1).limit(20))

        for d in duels:
            d['_id'] = str(d['_id'])

        return jsonify({"success": True, "duels": duels}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
