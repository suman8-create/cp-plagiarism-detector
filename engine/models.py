# engine/models.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# --- Test Case & Execution Entities ---

@dataclass
class TestCase:
    """Input and expected output pairs for code execution."""
    input_data: str
    expected_output: str
    is_sample: bool = False       # True if visible in problem description
    is_hidden: bool = True        # True if used for final submission evaluation
    explanation: Optional[str] = None


@dataclass
class ExecutionResult:
    """Runtime result of compiling and testing code against problem test cases."""
    status: str = "Pending"       # "Accepted", "Wrong Answer", "Compilation Error", "Time Limit Exceeded", "Runtime Error"
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None


# --- Domain Entity Classes ---

@dataclass
class Submission:
    """Represents a code submission for a problem/question."""
    submission_id: str
    problem_id: str
    user_id: str
    user_name: str
    source_file: str
    source_code: str
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: Optional[str] = None
    question_id: Optional[str] = None
    execution_result: ExecutionResult = field(default_factory=ExecutionResult)
    # Integrity & Plagiarism Metadata
    filtered_hashes: set[int] = field(default_factory=set)
    ai_confidence_score: float = 0.0
    ai_flags: List[str] = field(default_factory=list)


@dataclass
class Problem:
    """Represents a standalone coding problem with test cases and starter template."""
    problem_id: str
    title: str
    slug: str
    description: str
    difficulty: str = "Medium"     # "Easy", "Medium", "Hard"
    time_limit_sec: float = 2.0
    memory_limit_mb: int = 256
    starter_code: str = ""
    constraints: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    test_cases: List[TestCase] = field(default_factory=list)
    submissions: Dict[str, Submission] = field(default_factory=dict)
    boilerplate_hashes: set[int] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Question:
    """Legacy question container within an assessment (linked to Problem architecture)."""
    question_id: str
    assessment_id: str
    title: str
    description: str = ""
    submissions: Dict[str, Submission] = field(default_factory=dict)
    boilerplate_hashes: set[int] = field(default_factory=set)
    last_analyzed_at: Optional[datetime] = None


@dataclass
class Student:
    """Represents a student or user in the platform."""
    student_id: str
    name: str
    submission_ids: List[str] = field(default_factory=list)


@dataclass
class Assessment:
    """Assessment/Contest container."""
    assessment_id: str
    title: str
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    questions: Dict[str, Question] = field(default_factory=dict)
    students: Dict[str, Student] = field(default_factory=dict)


# --- Pydantic Schemas for REST API ---

class TestCaseSchema(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    explanation: Optional[str] = None


class CreateProblemRequest(BaseModel):
    title: str
    description: str
    difficulty: Optional[str] = "Medium"
    starter_code: Optional[str] = ""
    constraints: Optional[List[str]] = []
    examples: Optional[List[Dict[str, str]]] = []
    test_cases: Optional[List[TestCaseSchema]] = []


class ProblemSummaryResponse(BaseModel):
    problem_id: str
    title: str
    slug: str
    difficulty: str
    submission_count: int


class ProblemDetailResponse(BaseModel):
    problem_id: str
    title: str
    slug: str
    description: str
    difficulty: str
    time_limit_sec: float
    memory_limit_mb: int
    starter_code: str
    constraints: List[str]
    examples: List[Dict[str, str]]
    sample_test_cases: List[TestCaseSchema]
    submission_count: int


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