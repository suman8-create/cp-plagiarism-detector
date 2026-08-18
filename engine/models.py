# engine/models.py

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    status: str = "Pending"  # "Accepted", "Wrong Answer", "Compilation Error", "Time Limit Exceeded", "Runtime Error"
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None


class TestCase(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    is_hidden: bool = True
    explanation: Optional[str] = None


class Submission(BaseModel):
    submission_id: str
    problem_id: str
    user_id: str
    user_name: str
    source_file: str = "solution.cpp"
    source_code: str
    assessment_id: Optional[str] = None
    question_id: Optional[str] = None
    execution_result: ExecutionResult = Field(default_factory=ExecutionResult)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class Problem(BaseModel):
    problem_id: str
    title: str
    slug: str
    description: str
    difficulty: str = "Medium"  # "Easy", "Medium", "Hard"
    time_limit_sec: float = 2.0
    memory_limit_mb: int = 256
    starter_code: str = ""
    constraints: List[str] = Field(default_factory=list)
    examples: List[Dict[str, str]] = Field(default_factory=list)
    test_cases: List[TestCase] = Field(default_factory=list)
    submissions: Dict[str, Submission] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContestStatus(str, Enum):
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class ContestParticipant(BaseModel):
    user_id: str
    user_name: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    score: int = 0
    penalty_time_sec: float = 0.0
    solved_problem_ids: List[str] = Field(default_factory=list)


class Contest(BaseModel):
    contest_id: str
    title: str
    description: str = ""
    start_time: datetime
    duration_minutes: int = 90
    problem_ids: List[str] = Field(default_factory=list)
    participants: Dict[str, ContestParticipant] = Field(default_factory=dict)
    submissions: Dict[str, Submission] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def status(self) -> ContestStatus:
        now = datetime.utcnow()
        if now < self.start_time:
            return ContestStatus.UPCOMING
        elif now > self.end_time:
            return ContestStatus.ENDED
        return ContestStatus.ACTIVE


class Student(BaseModel):
    student_id: str
    name: str
    submission_ids: List[str] = Field(default_factory=list)


class Question(BaseModel):
    question_id: str
    assessment_id: str
    title: str
    description: str = ""
    submissions: Dict[str, Submission] = Field(default_factory=dict)
    last_analyzed_at: Optional[datetime] = None


class Assessment(BaseModel):
    assessment_id: str
    title: str
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    questions: Dict[str, Question] = Field(default_factory=dict)
    students: Dict[str, Student] = Field(default_factory=dict)


# --- API Request & Response Schemas ---

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
    constraints: Optional[List[str]] = Field(default_factory=list)
    examples: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    test_cases: Optional[List[TestCaseSchema]] = Field(default_factory=list)


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


class CreateContestRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    start_time_offset_min: int = 0
    duration_minutes: int = 90
    problem_ids: Optional[List[str]] = Field(default_factory=list)


class ContestSummaryResponse(BaseModel):
    contest_id: str
    title: str
    description: str
    status: str
    start_time: str
    end_time: str
    duration_minutes: int
    problem_count: int
    participant_count: int


class ContestDetailResponse(BaseModel):
    contest_id: str
    title: str
    description: str
    status: str
    start_time: str
    end_time: str
    duration_minutes: int
    problems: List[ProblemSummaryResponse]
    participant_count: int


class CreateAssessmentRequest(BaseModel):
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


class CreateQuestionRequest(BaseModel):
    title: str
    description: Optional[str] = ""


class QuestionSummaryResponse(BaseModel):
    question_id: str
    assessment_id: str
    title: str
    description: str
    submission_count: int
    is_analyzed: bool