from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

class BattleStatus(str, Enum):
    WAITING = "waiting"
    INBATTLE = "in_battle"
    FINISHED = "finished"

class QuestionModel(BaseModel):
    id: str = Field(..., description="ID ")
    text: str = Field(..., description=" la question")
    options: List[str] = Field(..., description="Liste des choix possibles")
    correct_answer: str = Field(..., description="La réponse correcte")
    points: int = Field(10, description="Points gagnés")
    category: str = Field(..., description="Catégorie de la question")

class QuizModel(BaseModel):
    id: str = Field(..., description="ID unique du quiz")
    title: str = Field(..., description="Titre du quiz")
    category: str = Field(..., description="Catégorie")
    difficulty: str = Field("medium", description="Niveau de difficulté")
    questions: List[QuestionModel] = Field(..., description="Liste des questions")

class UserAnswerModel(BaseModel):
    question_id: str = Field(..., description="L'ID ")
    selected_option: str = Field(..., description="L'option choisie par l'utilisateur")
    is_correct: bool = Field(..., description="la réponse est-elle juste ?")

class QuizResult(BaseModel):
    id: Optional[str] = Field(None, alias="_id") 
    clerk_id: str
    quiz_id: str
    score: int
    answers: List[UserAnswerModel] = Field(default_factory=list)

class BattleModel(BaseModel):
    id: str = Field(..., description="ID unique de la Battle") 
    quiz_id: str
    player1_id: str = Field(..., description="ID du créateur")
    player2_id: Optional[str] = Field(None, description="ID de l'adversaire")
    status: BattleStatus = Field(default=BattleStatus.WAITING)
    scores: Dict[str, int] = Field(default_factory=dict)
    winner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)