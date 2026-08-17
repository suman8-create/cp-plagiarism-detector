# engine/models.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# --- Domain Entity Classes ---

@dataclass
class Submission:
    """Represents a student's code submission for a specific question."""
    submission_id: str
    assessment_id: str
    question_id: str
    student_id: str
    student_name: str
    source_file: str
    source_code: str
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    # Populated after analysis
    filtered_hashes: set[int] = field(default_factory=set)
    ai_confidence_score: float = 0.0
    ai_flags: List[str] = field(default_factory=list)


@dataclass
class Question:
    """Represents an individual problem within an assessment."""
    question_id: str
    assessment_id: str
    title: str
    description: str = ""
    submissions: Dict[str, Submission] = field(default_factory=dict)  # submission_id -> Submission
    boilerplate_hashes: set[int] = field(default_factory=set)
    last_analyzed_at: Optional[datetime] = None


@dataclass
class Student:
    """Represents a student enrolled in/submitting to the assessment."""
    student_id: str
    name: str
    submission_ids: List[str] = field(default_factory=list)


@dataclass
class Assessment:
    """Top-level assessment container (e.g. Midterm Lab Exam)."""
    assessment_id: str
    title: str
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    questions: Dict[str, Question] = field(default_factory=dict)     # question_id -> Question
    students: Dict[str, Student] = field(default_factory=dict)       # student_id -> Student


# --- API Pydantic Request / Response Schemas ---

class CreateAssessmentRequest(BaseModel):
    title: str
    description: Optional[str] = ""


class CreateQuestionRequest(BaseModel):
    title: str
    description: Optional[str] = ""


class AssessmentSummaryResponse(BaseModel):
    assessment_id: str
    title: str
    description: str
    created_at: str
    question_count: int
    student_count: int
    total_submissions: int


class QuestionSummaryResponse(BaseModel):
    question_id: str
    assessment_id: str
    title: str
    description: str
    submission_count: int
    is_analyzed: bool