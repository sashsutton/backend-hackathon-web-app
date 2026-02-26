from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

class DuelStatus(str, Enum):
    WAITING = "waiting"
    INBATTLE = "in_battle"
    FINISHED = "finished"

class SoloSessionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class SoloGameSessionModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    quiz_id: str
    clerk_id: str
    status: SoloSessionStatus = Field(default=SoloSessionStatus.IN_PROGRESS)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[int] = None

class QuestionModel(BaseModel):
    id: Optional[int] = Field(None, description="ID (optionnel, auto-généré par MongoDB)")
    text: str = Field(..., description=" La question")
    options: List[str] = Field(..., description="Liste des choix possibles")
    correct_answer: str = Field(..., description="La réponse correcte")
    points: int = Field(10, description="Points gagnés")
    category: str = Field(..., description="Catégorie de la question")
    
    class Config:
        extra = "forbid"  # Empêche l'ajout de champs non définis

class QuizModel(BaseModel):
    id: Optional[int] = Field(None, description="ID unique du quiz (optionnel, généré par MongoDB)")
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

class DuelModel(BaseModel):
    id: str = Field(..., description="ID unique de la Battle") 
    quiz_id: str
    player1_id: str = Field(..., description="ID du créateur")
    player2_id: Optional[str] = Field(None, description="ID de l'adversaire")
    status: DuelStatus = Field(default=DuelStatus.WAITING)
    scores: Dict[str, int] = Field(default_factory=dict)
    winner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

