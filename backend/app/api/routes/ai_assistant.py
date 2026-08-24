from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.services.ai_assistant_service import AIAssistantService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class AskQuestionRequest(BaseModel):
    """Request to ask the AI assistant a question."""
    question: str
    context: Optional[dict] = None


class ExplainMetricRequest(BaseModel):
    """Request to explain a business metric."""
    metric: str


class AskQuestionResponse(BaseModel):
    """Response from AI assistant."""
    question: str
    answer: str
    confidence: float
    data_sources: List[str]
    recommendations: List[str]


class MetricExplanation(BaseModel):
    """Explanation of a business metric."""
    metric: str
    definition: str
    formula: str
    interpretation: str


class SuggestedQuestion(BaseModel):
    """A suggested question for the AI assistant."""
    question: str
    category: str
    description: str


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Ask the AI assistant a business question.

    The assistant will:
    1. Understand the question intent
    2. Identify required data and metrics
    3. Query the database
    4. Provide insights and recommendations
    """
    try:
        response = AIAssistantService.answer_question(
            db=db,
            question=request.question,
            context=request.context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=List[SuggestedQuestion])
async def get_suggestions(
    db: Session = Depends(get_db),
) -> list:
    """Get suggested questions for the AI assistant."""
    return AIAssistantService.get_suggested_questions(db)


@router.post("/explain-metric", response_model=MetricExplanation)
async def explain_metric(
    request: ExplainMetricRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Get explanation for a business metric."""
    explanation = AIAssistantService.explain_metric(db, request.metric)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Metric '{request.metric}' not found")
    return explanation
