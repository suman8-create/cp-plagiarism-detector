# engine/models.py

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionResult(BaseModel):
    status: str = "Pending"
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: float = 0.0
    memory_mb: float = 46.38
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
    problem_title: str = ""
    user_id: str
    user_name: str
    source_file: str = "solution.cpp"
    source_code: str = ""
    contest_id: Optional[str] = None
    time_taken_seconds: float = 0.0
    execution_result: ExecutionResult = Field(default_factory=ExecutionResult)
    submitted_at: datetime = Field(default_factory=get_utc_now)


class Problem(BaseModel):
    problem_id: str
    title: str
    slug: str
    category: str = "Algorithms"
    topic_tags: List[str] = Field(default_factory=list)
    description: str
    difficulty: str = "Medium"
    time_limit_sec: float = 2.0
    memory_limit_mb: int = 256
    starter_code: str = ""
    constraints: List[str] = Field(default_factory=list)
    examples: List[Dict[str, str]] = Field(default_factory=list)
    test_cases: List[TestCase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=get_utc_now)


class ContestStatus(str, Enum):
    UPCOMING = "Upcoming"
    LIVE = "Live"
    FINISHED = "Finished"

class ContestParticipant(BaseModel):
    user_id: str
    user_name: str
    score: int = 0
    penalty_time_sec: float = 0.0
    solved_problem_ids: List[str] = Field(default_factory=list)
    solved_timestamps: Dict[str, str] = Field(default_factory=dict)
    disqualified: bool = False
    disqualification_reason: Optional[str] = None


class Contest(BaseModel):
    contest_id: str
    title: str
    description: str = ""
    start_time: datetime
    duration_minutes: int = 90
    problem_ids: List[str] = Field(default_factory=list)
    participants: Dict[str, ContestParticipant] = Field(default_factory=dict)
    submissions: Dict[str, Submission] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=get_utc_now)

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def status(self) -> ContestStatus:
        now = get_utc_now()
        st = self.start_time if self.start_time.tzinfo else self.start_time.replace(tzinfo=timezone.utc)
        et = self.end_time if self.end_time.tzinfo else self.end_time.replace(tzinfo=timezone.utc)

        if now < st:
            return ContestStatus.UPCOMING
        elif now > et:
            return ContestStatus.FINISHED
        return ContestStatus.LIVE


# --- API Schemas ---

class TestCaseSchema(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    explanation: Optional[str] = None


class CreateProblemRequest(BaseModel):
    title: str
    description: str
    difficulty: Optional[str] = "Medium"
    category: Optional[str] = "Algorithms"
    topic_tags: Optional[List[str]] = Field(default_factory=list)
    starter_code: Optional[str] = ""
    constraints: Optional[List[str]] = Field(default_factory=list)
    examples: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    test_cases: Optional[List[TestCaseSchema]] = Field(default_factory=list)


class ProblemSummaryResponse(BaseModel):
    problem_id: str
    title: str
    slug: str
    difficulty: str
    category: str = "Algorithms"
    topic_tags: List[str] = Field(default_factory=list)
    acceptance_rate: float = 65.4
    submission_count: int = 0
    is_solved: bool = False


class ProblemDetailResponse(BaseModel):
    problem_id: str
    title: str
    slug: str
    description: str
    difficulty: str
    category: str
    topic_tags: List[str]
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
    user_registered: bool = False
    user_score: int = 0
    user_solved_count: int = 0
    user_penalty_minutes: float = 0.0


class SubmissionRecordResponse(BaseModel):
    submission_id: str
    problem_id: str
    problem_title: str = ""
    user_id: str
    user_name: str
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: float
    memory_mb: float = 46.38
    time_taken_seconds: float = 0.0
    source_code: str = ""
    error_message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    submitted_at: str


class LeaderboardProblemCell(BaseModel):
    problem_id: str
    status: str
    attempts_count: int
    solved_time_min: Optional[float] = None


class LeaderboardRow(BaseModel):
    rank: int
    user_id: str
    user_name: str
    score: int
    penalty_time_sec: float
    solved_problems: List[str] = Field(default_factory=list)
    disqualified: bool = False
    disqualification_reason: Optional[str] = None


class ContestLeaderboardResponse(BaseModel):
    contest_id: str
    contest_title: str
    rows: List[LeaderboardRow] = Field(default_factory=list)


class UserProfileStats(BaseModel):
    user_id: str
    user_name: str
    handle: str
    total_solved: int
    total_problems: int
    easy_solved: int
    easy_total: int
    medium_solved: int
    medium_total: int
    hard_solved: int
    hard_total: int
    accuracy_percentage: float
    total_submissions: int
    skills_breakdown: Dict[str, int] = Field(default_factory=dict)
    recent_submissions: List[SubmissionRecordResponse] = Field(default_factory=list)


class IntegrityReport(BaseModel):
    similarity_score: float = 0.0
    matched_submission_id: Optional[str] = None
    matched_user_name: Optional[str] = None
    ai_probability: float = 0.0
    ai_risk_level: str = "Low"  # "Clean" | "Low" | "Medium" | "High"
    verdict: str = "Clean"       # "Clean" | "Suspicious Similarity" | "High AI Probability" | "Plagiarized"
    forensic_flags: List[str] = Field(default_factory=list)


# Update ExecutionResult to include integrity_report:
class ExecutionResult(BaseModel):
    status: str = "Pending"
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: float = 0.0
    memory_mb: float = 46.38
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None
    integrity_report: Optional[IntegrityReport] = None


# Update SubmissionRecordResponse to include integrity_report:
class SubmissionRecordResponse(BaseModel):
    submission_id: str
    problem_id: str
    problem_title: str = ""
    user_id: str
    user_name: str
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: float
    memory_mb: float = 46.38
    time_taken_seconds: float = 0.0
    source_code: str = ""
    error_message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    integrity_report: Optional[IntegrityReport] = None
    submitted_at: str

class SubmitSolutionRequest(BaseModel):
    source_code: str
    user_id: str
    user_name: str = "Competitor"
    contest_id: Optional[str] = None
    time_taken_seconds: float = 0.0

class SuspectPair(BaseModel):
    user_a_id: str
    user_a_name: str
    user_b_id: str
    user_b_name: str
    problem_id: str
    problem_title: str
    ast_similarity: float
    time_delta_seconds: float
    suspicion_score: float  # Composite score incorporating AST similarity + temporal proximity
    status: str = "FLAGGED"  # "FLAGGED" | "CONFIRMED" | "DISMISSED" | "DISQUALIFIED"
    user_a_sub_id: str
    user_b_sub_id: str
    user_a_code: str
    user_b_code: str
    flags: List[str] = Field(default_factory=list)


class ContestSimilarityMatrix(BaseModel):
    problem_id: str
    problem_title: str
    participant_ids: List[str] = Field(default_factory=list)
    participant_names: List[str] = Field(default_factory=list)
    matrix: List[List[float]] = Field(default_factory=list)  # N x N pairwise similarity matrix


class ContestAuditReport(BaseModel):
    contest_id: str
    contest_title: str
    audited_at: str
    total_participants: int
    total_submissions_audited: int
    flagged_pairs_count: int
    similarity_matrices: List[ContestSimilarityMatrix] = Field(default_factory=list)
    suspect_pairs: List[SuspectPair] = Field(default_factory=list)

class AdminDecisionAction(str, Enum):
    FLAG_FOR_REVIEW = "FLAGGED"
    CONFIRM_COLLUSION = "CONFIRMED"
    DISQUALIFY = "DISQUALIFIED"
    CLEAR_FALSE_POSITIVE = "CLEARED"

class AdminDecisionRequest(BaseModel):
    contest_id: str
    problem_id: str
    user_id: str
    partner_user_id: Optional[str] = None
    action: AdminDecisionAction
    reason: str = "Administrative review of code similarity and temporal metrics."
    admin_id: str = "admin_root_01"

class LeaderboardRankRecalcResponse(BaseModel):
    contest_id: str
    status: str
    disqualified_users: List[str]
    recalculated_leaderboard: List[ContestParticipant]
    updated_at: str

class Example(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None 

class User(BaseModel):
    user_id: str
    username: str
    display_name: str
    password_hash: str
    role: str = "participant"  # "participant" | "admin"
    created_at: Optional[datetime] = None