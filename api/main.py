# api/main.py

import io
import zipfile
import traceback
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.detector import PlagiarismDetector
from engine.forensics import LLMForensicEngine
from engine.runner import CppExecutionEngine
from engine.models import (
    ContestDetailResponse,
    ContestLeaderboardResponse,
    ContestStatus,
    ContestSummaryResponse,
    CreateContestRequest,
    CreateProblemRequest,
    ProblemDetailResponse,
    ProblemSummaryResponse,
    SubmissionRecordResponse,
    TestCase,
    TestCaseSchema,
    UserProfileStats,
)
from engine.repository import AssessmentRepository

app = FastAPI(
    title="Competitive Programming & Code Integrity Platform API",
    description="Competitive coding platform with integrated AST plagiarism detector & LLM forensic engine",
    version="4.1.0",
)

detector_engine = PlagiarismDetector()
forensic_engine = LLMForensicEngine()
exec_runner = CppExecutionEngine()
repo = AssessmentRepository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth Request Schemas ---

class RegisterRequest(BaseModel):
    username: str
    display_name: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    user_id: str
    username: str
    display_name: str


# --- Execution & Submission Schemas ---

class CodeRunRequest(BaseModel):
    source_code: str
    user_id: Optional[str] = "std_suman_01"
    user_name: Optional[str] = "Suman"
    contest_id: Optional[str] = None
    time_taken_seconds: Optional[float] = 0.0


class CodeExecutionResponse(BaseModel):
    submission_id: Optional[str] = None
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: float
    memory_mb: float = 46.38
    time_taken_seconds: float = 0.0
    stdout: str
    stderr: str
    error_message: Optional[str] = None
    submitted_at: Optional[str] = None


# --- Plagiarism & Forensics Schemas ---

class MatchSpanModel(BaseModel):
    start_line: int
    end_line: int


class ComparisonResultModel(BaseModel):
    file_a: str
    file_b: str
    similarity_score: float
    shared_fingerprints_count: int
    matched_lines_a: List[MatchSpanModel]
    matched_lines_b: List[MatchSpanModel]


class ForensicReportModel(BaseModel):
    ai_confidence_score: float
    is_suspicious: bool
    flags: List[str]


class AnalysisResponse(BaseModel):
    total_files_analyzed: int
    boilerplate_hashes_filtered: int
    comparisons: List[ComparisonResultModel]
    files_content: Dict[str, str]
    file_boilerplate_spans: Dict[str, List[MatchSpanModel]]
    forensics: Dict[str, ForensicReportModel]


class TemplateStatsResponse(BaseModel):
    total_files_evaluated: int
    boilerplate_hashes_count: int
    frequency_threshold: float
    minimum_file_threshold: int


# --- Root & System Health ---

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Competitive Programming & Code Integrity Platform",
        "version": "4.1.0",
    }


# --- Auth Endpoints ---

@app.post("/api/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest):
    try:
        user = repo.register_user(req.username, req.display_name, req.password)
        return AuthResponse(
            user_id=user["user_id"],
            username=user["username"],
            display_name=user["display_name"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: LoginRequest):
    user = repo.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return AuthResponse(
        user_id=user["user_id"],
        username=user["username"],
        display_name=user["display_name"],
    )


# --- Profile Stats API ---

@app.get("/api/users/{user_id}/profile", response_model=UserProfileStats)
def get_user_profile(user_id: str, user_name: Optional[str] = None, handle: Optional[str] = None):
    try:
        return repo.get_user_profile_stats(user_id, fallback_name=user_name, fallback_handle=handle)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- Contest API Endpoints ---

@app.get("/api/contests", response_model=List[ContestSummaryResponse])
def list_contests():
    contests = repo.list_contests()
    return [
        ContestSummaryResponse(
            contest_id=c.contest_id,
            title=c.title,
            description=c.description,
            status=c.status.value,
            start_time=c.start_time.isoformat(),
            end_time=c.end_time.isoformat(),
            duration_minutes=c.duration_minutes,
            problem_count=len(c.problem_ids),
            participant_count=len(c.participants),
        )
        for c in contests
    ]


@app.get("/api/contests/{contest_id}", response_model=ContestDetailResponse)
def get_contest(contest_id: str, user_id: str = "std_suman_01"):
    c = repo.get_contest(contest_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contest not found")

    is_registered = user_id in c.participants
    participant = c.participants.get(user_id)
    user_solved_ids = set(participant.solved_problem_ids) if participant else set()

    problems_list = []
    for pid in c.problem_ids:
        prob = repo.get_problem(pid)
        if prob:
            is_prob_solved = (prob.problem_id in user_solved_ids) or (prob.slug in user_solved_ids)
            problems_list.append(
                ProblemSummaryResponse(
                    problem_id=prob.problem_id,
                    title=prob.title,
                    slug=prob.slug,
                    difficulty=prob.difficulty,
                    category=prob.category,
                    topic_tags=prob.topic_tags,
                    is_solved=is_prob_solved,
                )
            )

    user_solved_count = sum(1 for p in problems_list if p.is_solved)

    return ContestDetailResponse(
        contest_id=c.contest_id,
        title=c.title,
        description=c.description,
        status=c.status.value,
        start_time=c.start_time.isoformat(),
        end_time=c.end_time.isoformat(),
        duration_minutes=c.duration_minutes,
        problems=problems_list,
        participant_count=len(c.participants),
        user_registered=is_registered,
        user_score=user_solved_count * 100,
        user_solved_count=user_solved_count,
        user_penalty_minutes=round(participant.penalty_time_sec / 60.0, 1) if participant else 0.0,
    )


@app.get("/api/contests/{contest_id}/leaderboard", response_model=ContestLeaderboardResponse)
def get_contest_leaderboard(contest_id: str):
    board = repo.get_contest_leaderboard(contest_id)
    if not board:
        raise HTTPException(status_code=404, detail="Contest not found")
    return board


@app.post("/api/contests", response_model=ContestDetailResponse)
def create_contest(req: CreateContestRequest):
    start = datetime.now(timezone.utc) + timedelta(minutes=req.start_time_offset_min)
    contest = repo.create_contest(
        title=req.title,
        description=req.description or "",
        start_time=start,
        duration_minutes=req.duration_minutes,
        problem_ids=req.problem_ids or [p.problem_id for p in repo.list_problems()],
    )

    problems_list = [
        ProblemSummaryResponse(
            problem_id=p.problem_id,
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            category=p.category,
            topic_tags=p.topic_tags,
            is_solved=False,
        )
        for pid in contest.problem_ids
        if (p := repo.get_problem(pid))
    ]

    return ContestDetailResponse(
        contest_id=contest.contest_id,
        title=contest.title,
        description=contest.description,
        status=contest.status.value,
        start_time=contest.start_time.isoformat(),
        end_time=contest.end_time.isoformat(),
        duration_minutes=contest.duration_minutes,
        problems=problems_list,
        participant_count=0,
        user_registered=False,
        user_score=0,
        user_solved_count=0,
        user_penalty_minutes=0.0,
    )


@app.post("/api/contests/{contest_id}/register")
def register_for_contest(contest_id: str, user_id: str = "std_suman_01", user_name: str = "Suman"):
    participant = repo.register_contest_participant(contest_id, user_id, user_name)
    if not participant:
        raise HTTPException(status_code=404, detail="Contest not found")
    return {"message": "Successfully registered for contest", "user_id": user_id, "user_name": user_name}


# --- Problem Platform Endpoints ---

@app.get("/api/problems", response_model=List[ProblemSummaryResponse])
def list_problems(user_id: Optional[str] = None):
    problems = repo.list_problems()
    user_subs = repo.get_user_submissions(user_id) if (user_id and user_id != 'null' and user_id != 'guest_user') else []
    
    solved_keys = set()
    for s in user_subs:
        if s.execution_result and s.execution_result.status == "Accepted":
            solved_keys.add(s.problem_id)
            prob_obj = repo.get_problem(s.problem_id)
            if prob_obj:
                solved_keys.add(prob_obj.slug)
                solved_keys.add(prob_obj.problem_id)

    return [
        ProblemSummaryResponse(
            problem_id=p.problem_id,
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            category=p.category,
            topic_tags=p.topic_tags,
            acceptance_rate=65.4,
            submission_count=len(repo.get_problem_submissions(p.problem_id)),
            is_solved=(p.problem_id in solved_keys or p.slug in solved_keys),
        )
        for p in problems
    ]

@app.get("/api/problems/{problem_id_or_slug}", response_model=ProblemDetailResponse)
def get_problem(problem_id_or_slug: str):
    p = repo.get_problem(problem_id_or_slug)
    if not p:
        raise HTTPException(status_code=404, detail="Problem not found")

    sample_tests = [
        TestCaseSchema(
            input_data=t.input_data,
            expected_output=t.expected_output,
            is_sample=t.is_sample,
            explanation=t.explanation,
        )
        for t in p.test_cases
        if t.is_sample
    ]

    return ProblemDetailResponse(
        problem_id=p.problem_id,
        title=p.title,
        slug=p.slug,
        description=p.description,
        difficulty=p.difficulty,
        category=p.category,
        topic_tags=p.topic_tags,
        time_limit_sec=p.time_limit_sec,
        memory_limit_mb=p.memory_limit_mb,
        starter_code=p.starter_code,
        constraints=p.constraints,
        examples=p.examples,
        sample_test_cases=sample_tests,
        submission_count=len(repo.get_problem_submissions(p.problem_id)),
    )


# --- Execution & Submissions Endpoints ---

@app.post("/api/problems/{problem_id_or_slug}/run", response_model=CodeExecutionResponse)
def run_sample_cases(problem_id_or_slug: str, req: CodeRunRequest):
    problem = repo.get_problem(problem_id_or_slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    sample_cases = [tc for tc in problem.test_cases if tc.is_sample]
    if not sample_cases:
        sample_cases = problem.test_cases[:1]

    result = exec_runner.execute(
        source_code=req.source_code,
        test_cases=sample_cases,
        time_limit_sec=problem.time_limit_sec,
    )

    return CodeExecutionResponse(
        status=result.status,
        passed_test_cases=result.passed_test_cases,
        total_test_cases=result.total_test_cases,
        execution_time_ms=result.execution_time_ms,
        memory_mb=46.38,
        time_taken_seconds=req.time_taken_seconds or 0.0,
        stdout=result.stdout,
        stderr=result.stderr,
        error_message=result.error_message,
    )


@app.post("/api/problems/{problem_id_or_slug}/submit", response_model=CodeExecutionResponse)
def submit_solution(problem_id_or_slug: str, req: CodeRunRequest):
    problem = repo.get_problem(problem_id_or_slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if req.contest_id:
        contest = repo.get_contest(req.contest_id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        if contest.status == ContestStatus.FINISHED:
            raise HTTPException(status_code=400, detail="Contest has ended. Submissions are closed.")
        if contest.status == ContestStatus.UPCOMING:
            raise HTTPException(status_code=400, detail="Contest has not started yet.")

    result = exec_runner.execute(
        source_code=req.source_code,
        test_cases=problem.test_cases,
        time_limit_sec=problem.time_limit_sec,
    )

    submission = repo.save_submission(
        problem_id=problem.problem_id,
        user_id=req.user_id or "std_suman_01",
        user_name=req.user_name or "Suman",
        source_code=req.source_code,
        time_taken_seconds=req.time_taken_seconds or 0.0,
        execution_result=result,
        contest_id=req.contest_id,
    )

    return CodeExecutionResponse(
        submission_id=submission.submission_id,
        status=result.status,
        passed_test_cases=result.passed_test_cases,
        total_test_cases=result.total_test_cases,
        execution_time_ms=result.execution_time_ms,
        memory_mb=46.38,
        time_taken_seconds=submission.time_taken_seconds,
        stdout=result.stdout,
        stderr=result.stderr,
        error_message=result.error_message,
        submitted_at=submission.submitted_at.isoformat(),
    )


@app.get("/api/problems/{problem_id_or_slug}/submissions", response_model=List[SubmissionRecordResponse])
def get_problem_submissions(problem_id_or_slug: str):
    submissions = repo.get_problem_submissions(problem_id_or_slug)
    return [
        SubmissionRecordResponse(
            submission_id=s.submission_id,
            problem_id=s.problem_id,
            problem_title=s.problem_title,
            user_id=s.user_id,
            user_name=s.user_name,
            status=s.execution_result.status,
            passed_test_cases=s.execution_result.passed_test_cases,
            total_test_cases=s.execution_result.total_test_cases,
            execution_time_ms=s.execution_result.execution_time_ms,
            memory_mb=s.execution_result.memory_mb or 46.38,
            time_taken_seconds=s.time_taken_seconds,
            source_code=s.source_code,
            error_message=s.execution_result.error_message,
            stdout=s.execution_result.stdout,
            stderr=s.execution_result.stderr,
            submitted_at=s.submitted_at.isoformat(),
        )
        for s in submissions
    ]


# --- Plagiarism & Forensics Endpoint ---

@app.post("/api/check-plagiarism", response_model=AnalysisResponse)
@app.post("/api/analyze", response_model=AnalysisResponse)
async def check_plagiarism(files: List[UploadFile] = File(...)):
    submissions: Dict[str, str] = {}

    for uploaded_file in files:
        content_bytes = await uploaded_file.read()
        filename = uploaded_file.filename

        if filename.endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(content_bytes)) as z:
                    for zip_info in z.infolist():
                        if zip_info.filename.endswith((".cpp", ".cc", ".cxx", ".h")):
                            if "__MACOSX" in zip_info.filename or zip_info.is_dir():
                                continue
                            file_str = z.read(zip_info).decode("utf-8", errors="ignore")
                            clean_name = zip_info.filename.split("/")[-1]
                            submissions[clean_name] = file_str
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read ZIP archive: {str(e)}")

        elif filename.endswith((".cpp", ".cc", ".cxx", ".h")):
            try:
                submissions[filename] = content_bytes.decode("utf-8", errors="ignore")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to decode {filename}: {str(e)}")

    if len(submissions) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 C++ files to perform pairwise comparison.",
        )

    results, boilerplate, boilerplate_spans = detector_engine.analyze_submissions(submissions)

    forensics_data: Dict[str, ForensicReportModel] = {}
    for fname, code in submissions.items():
        report = forensic_engine.scan(code)
        forensics_data[fname] = ForensicReportModel(
            ai_confidence_score=report.ai_confidence_score,
            is_suspicious=report.is_suspicious,
            flags=report.flags,
        )

    comparisons = [
        ComparisonResultModel(
            file_a=res.file_a,
            file_b=res.file_b,
            similarity_score=res.similarity_score,
            shared_fingerprints_count=res.shared_fingerprints_count,
            matched_lines_a=[MatchSpanModel(start_line=m.start_line, end_line=m.end_line) for m in res.matched_lines_a],
            matched_lines_b=[MatchSpanModel(start_line=m.start_line, end_line=m.end_line) for m in res.matched_lines_b],
        )
        for res in results
    ]

    formatted_boilerplate_spans = {
        fname: [MatchSpanModel(start_line=s.start_line, end_line=s.end_line) for s in spans]
        for fname, spans in boilerplate_spans.items()
    }

    return AnalysisResponse(
        total_files_analyzed=len(submissions),
        boilerplate_hashes_filtered=len(boilerplate),
        comparisons=comparisons,
        files_content=submissions,
        file_boilerplate_spans=formatted_boilerplate_spans,
        forensics=forensics_data,
    )