from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.database import get_db
from app.services.ai_assistant_service import AIAssistantService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class AskQuestionRequest(BaseModel):
    """Request to ask the AI assistant a question."""
    question: str
    context: Optional[dict] = None
    session_id: Optional[str] = None


class ExplainMetricRequest(BaseModel):
    """Request to explain a business metric."""
    metric: str


class SourceRef(BaseModel):
    """One data source backing an answer - a database query or a knowledge-base document."""
    type: str  # "database" | "document"
    source: str
    sheet: Optional[str] = None


class AskQuestionResponse(BaseModel):
    """Response from AI assistant."""
    question: str
    answer: str
    confidence: float
    data_sources: List[str]
    recommendations: List[str]
    route: Optional[str] = None  # "SQL" | "RAG" | "HYBRID" | "CLARIFICATION"
    sources: List[SourceRef] = []


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
    1. Understand the question intent using Groq AI
    2. Identify required data and metrics
    3. Query the database
    4. Provide insights and recommendations
    5. Support multi-turn conversations with session_id
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        response = AIAssistantService.answer_question(
            db=db,
            question=request.question,
            context=request.context,
            session_id=request.session_id
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing your question: {str(e)}")


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
