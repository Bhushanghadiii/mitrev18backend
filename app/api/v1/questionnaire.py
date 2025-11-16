from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os
import json
from app.database import get_db
from app.models.tenant import User
from app.models.assessment import QuestionnaireResponse
from app.utils.security import get_current_user


router = APIRouter()

class QuestionResponse(BaseModel):
    question_id: str
    capability_type: str
    has_capability: bool
    coverage_level: int
    platforms_covered: List[str]
    notes: str = ""

class SubmitQuestionnaireRequest(BaseModel):
    assessment_id: int
    responses: List[QuestionResponse]

@router.get("/questions")
async def get_questions():
    # Load from fixed JSON file
    json_path = os.path.join(os.path.dirname(__file__), "../../data/questionnaire_v18.json")
    with open(os.path.abspath(json_path), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@router.post("/submit")
async def submit_questionnaire(request: SubmitQuestionnaireRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Save all responses
    for response in request.responses:
        qr = QuestionnaireResponse(
            assessment_id=request.assessment_id,
            question_id=response.question_id,
            capability_type=response.capability_type,
            has_capability=response.has_capability,
            coverage_level=response.coverage_level,
            platforms_covered=response.platforms_covered,
            notes=response.notes
        )
        db.add(qr)
    db.commit()
    return {"message": "Questionnaire submitted successfully", "responses_count": len(request.responses)}
