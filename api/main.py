# api/main.py

import io
import zipfile
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
    ContestStatus,
    ContestSummaryResponse,
    CreateContestRequest,
    CreateProblemRequest,
    ProblemDetailResponse,
    ProblemSummaryResponse,
    SubmissionRecordResponse,
    TestCase,
    TestCaseSchema,
)
from engine.repository import AssessmentRepository

app = FastAPI(
    title="Competitive Programming & Code Integrity Platform API",
    description="Competitive coding platform with integrated AST plagiarism detector & LLM forensic engine",
    version="3.1.0",
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


# --- Execution & Submission API Schemas ---

class CodeRunRequest(BaseModel):
    source_code: str
    user_id: Optional[str] = "std_demo_101"
    user_name: Optional[str] = "Alex Developer"
    contest_id: Optional[str] = None


class CodeExecutionResponse(BaseModel):
    submission_id: Optional[str] = None
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: float
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
        "version": "3.1.0",
    }


@app.get("/api/template-stats", response_model=TemplateStatsResponse)
def get_template_stats():
    stats = detector_engine.last_boilerplate_stats
    if not stats:
        return TemplateStatsResponse(
            total_files_evaluated=0,
            boilerplate_hashes_count=0,
            frequency_threshold=detector_engine.boilerplate_threshold,
            minimum_file_threshold=3,
        )
    return TemplateStatsResponse(
        total_files_evaluated=stats.get("total_files", 0),
        boilerplate_hashes_count=stats.get("boilerplate_hashes_count", 0),
        frequency_threshold=stats.get("threshold_used", 0.50),
        minimum_file_threshold=stats.get("min_file_threshold", 3),
    )


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
def get_contest(contest_id: str, user_id: str = "std_demo_101"):
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
            problems_list.append(
                ProblemSummaryResponse(
                    problem_id=prob.problem_id,
                    title=prob.title,
                    slug=prob.slug,
                    difficulty=prob.difficulty,
                    submission_count=len(prob.submissions),
                    is_solved=(prob.problem_id in user_solved_ids),
                )
            )

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
        user_score=participant.score if participant else 0,
        user_solved_count=len(user_solved_ids),
        user_penalty_minutes=round(participant.penalty_time_sec / 60.0, 1) if participant else 0.0,
    )


@app.post("/api/contests", response_model=ContestDetailResponse)
def create_contest(req: CreateContestRequest):
    start = datetime.now(timezone.utc) + timedelta(minutes=req.start_time_offset_min)
    contest = repo.create_contest(
        title=req.title,
        description=req.description or "",
        start_time=start,
        duration_minutes=req.duration_minutes,
        problem_ids=req.problem_ids or list(repo._problems.keys()),
    )

    problems_list = [
        ProblemSummaryResponse(
            problem_id=p.problem_id,
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            submission_count=len(p.submissions),
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
def register_for_contest(contest_id: str, user_id: str = "std_demo_101", user_name: str = "Alex Developer"):
    participant = repo.register_contest_participant(contest_id, user_id, user_name)
    if not participant:
        raise HTTPException(status_code=404, detail="Contest not found")
    return {"message": "Successfully registered for contest", "user_id": user_id}


# --- Problem Platform Endpoints ---

@app.get("/api/problems", response_model=List[ProblemSummaryResponse])
def list_problems():
    problems = repo.list_problems()
    return [
        ProblemSummaryResponse(
            problem_id=p.problem_id,
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            submission_count=len(p.submissions),
            is_solved=False,
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
        time_limit_sec=p.time_limit_sec,
        memory_limit_mb=p.memory_limit_mb,
        starter_code=p.starter_code,
        constraints=p.constraints,
        examples=p.examples,
        sample_test_cases=sample_tests,
        submission_count=len(p.submissions),
    )


@app.post("/api/problems", response_model=ProblemDetailResponse)
def create_problem(req: CreateProblemRequest):
    test_cases = [
        TestCase(
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            is_sample=tc.is_sample,
            is_hidden=not tc.is_sample,
            explanation=tc.explanation,
        )
        for tc in (req.test_cases or [])
    ]

    problem = repo.create_problem(
        title=req.title,
        description=req.description,
        difficulty=req.difficulty or "Medium",
        starter_code=req.starter_code or "",
        constraints=req.constraints or [],
        examples=req.examples or [],
        test_cases=test_cases,
    )

    sample_tests = [
        TestCaseSchema(
            input_data=t.input_data,
            expected_output=t.expected_output,
            is_sample=t.is_sample,
            explanation=t.explanation,
        )
        for t in problem.test_cases
        if t.is_sample
    ]

    return ProblemDetailResponse(
        problem_id=problem.problem_id,
        title=problem.title,
        slug=problem.slug,
        description=problem.description,
        difficulty=problem.difficulty,
        time_limit_sec=problem.time_limit_sec,
        memory_limit_mb=problem.memory_limit_mb,
        starter_code=problem.starter_code,
        constraints=problem.constraints,
        examples=problem.examples,
        sample_test_cases=sample_tests,
        submission_count=0,
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
        stdout=result.stdout,
        stderr=result.stderr,
        error_message=result.error_message,
    )


@app.post("/api/problems/{problem_id_or_slug}/submit", response_model=CodeExecutionResponse)
def submit_solution(problem_id_or_slug: str, req: CodeRunRequest):
    problem = repo.get_problem(problem_id_or_slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Contest Gating
    if req.contest_id:
        contest = repo.get_contest(req.contest_id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        if contest.status == ContestStatus.FINISHED:
            raise HTTPException(status_code=400, detail="Contest has ended. Submissions are closed.")
        if contest.status == ContestStatus.UPCOMING:
            raise HTTPException(status_code=400, detail="Contest has not started yet.")

    # 1. Run full test case suite
    result = exec_runner.execute(
        source_code=req.source_code,
        test_cases=problem.test_cases,
        time_limit_sec=problem.time_limit_sec,
    )

    # 2. Persist submission
    submission = repo.save_submission(
        problem_id=problem.problem_id,
        user_id=req.user_id or "std_demo_101",
        user_name=req.user_name or "Alex Developer",
        source_code=req.source_code,
        execution_result=result,
        contest_id=req.contest_id,
    )

    return CodeExecutionResponse(
        submission_id=submission.submission_id,
        status=result.status,
        passed_test_cases=result.passed_test_cases,
        total_test_cases=result.total_test_cases,
        execution_time_ms=result.execution_time_ms,
        stdout=result.stdout,
        stderr=result.stderr,
        error_message=result.error_message,
        submitted_at=submission.submitted_at.isoformat(),
    )


@app.get("/api/problems/{problem_id_or_slug}/submissions", response_model=List[SubmissionRecordResponse])
def get_problem_submissions(problem_id_or_slug: str):
    problem = repo.get_problem(problem_id_or_slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    submissions = repo.get_problem_submissions(problem.problem_id)
    return [
        SubmissionRecordResponse(
            submission_id=s.submission_id,
            problem_id=s.problem_id,
            user_id=s.user_id,
            user_name=s.user_name,
            status=s.execution_result.status,
            passed_test_cases=s.execution_result.passed_test_cases,
            total_test_cases=s.execution_result.total_test_cases,
            execution_time_ms=s.execution_result.execution_time_ms,
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