from typing import List, Dict, Any
from models.quiz_models import UserAnswerModel, QuizResult
from pymongo.database import Database
from bson import ObjectId

class QuizService:
    def __init__(self, db: Database):
        self.db = db
    
    def calculate_quiz_score(self, quiz_id: str, user_answers: List[UserAnswerModel]) -> QuizResult:
        """
        Calculer le score pour un quiz !!!!
        
        Args:
            quiz_id: The ID of the quiz
            user_answers: List of user answers
            
        Returns:
            QuizResult object with calculated score and detailed answers
        """

        original_quiz = self.db.quizzes.find_one({"id": quiz_id})
        if not original_quiz:
            raise ValueError("Quiz not found")
        
        total_score = 0
        detailed_answers = []
        

        for user_ans in user_answers:
            question = next((q for q in original_quiz['questions'] if q['id'] == user_ans.question_id), None)
            
            if question:
                is_correct = (user_ans.selected_option == question['correct_answer'])
                if is_correct:
                    total_score += question['points']
                
                detailed_answers.append({
                    "question_id": question['id'],
                    "selected_option": user_ans.selected_option,
                    "is_correct": is_correct
                })
        
        return QuizResult(
            clerk_id="",
            quiz_id=quiz_id,
            score=total_score,
            answers=detailed_answers
        )
    
    def save_quiz_result(self, result: QuizResult) -> str:
        """
        Save quiz result to database.
        
        Args:
            result: QuizResult object to save
            
        Returns:
            Inserted document ID
        """
        result_dict = result.model_dump(exclude={'id'})
        insert_result = self.db.results.insert_one(result_dict)
        return str(insert_result.inserted_id)
    
    def get_quiz_by_id(self, quiz_id: str) -> Dict[str, Any]:
        """
        Get quiz by ID, excluding correct answers.
        
        Args:
            quiz_id: The ID of the quiz
            
        Returns:
            Quiz data without correct answers
        """
        quiz_data = self.db.quizzes.find_one({"id": quiz_id}, {"_id": 0})
        if not quiz_data:
            raise ValueError("Quiz not found")
        
        # Remove correct answers from questions
        for q in quiz_data['questions']:
            del q['correct_answer']
        
        return quiz_data
    
    def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """
        Get all quizzes with basic information.
        
        Returns:
            List of quizzes with id, title, and category
        """
        quizzes = list(self.db.quizzes.find({}, {"_id": 1, "title": 1, "category": 1}))
        # Convert ObjectId to string
        for q in quizzes:
            q['_id'] = str(q['_id'])
        return quizzes