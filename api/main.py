# api/main.py

import io
import zipfile
from typing import Dict, List
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.detector import PlagiarismDetector
from engine.forensics import LLMForensicEngine
from engine.models import (
    AssessmentSummaryResponse,
    CreateAssessmentRequest,
    CreateQuestionRequest,
    QuestionSummaryResponse,
)
from engine.repository import AssessmentRepository

app = FastAPI(
    title="Code Assessment Integrity Platform API",
    description="AST-based code assessment integrity & LLM forensic engine",
    version="2.0.0",
)

# Global engine and data repository instances
detector_engine = PlagiarismDetector()
forensic_engine = LLMForensicEngine()
repo = AssessmentRepository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Response Schemas ---
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


# --- System & Baseline Routes ---

@app.get("/")
def health_check():
    return {"status": "online", "service": "Code Assessment Integrity Platform"}


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


# --- Assessment Management Routes (New in Phase 1) ---

@app.post("/api/assessments", response_model=AssessmentSummaryResponse)
def create_assessment(req: CreateAssessmentRequest):
    asm = repo.create_assessment(title=req.title, description=req.description or "")
    return AssessmentSummaryResponse(
        assessment_id=asm.assessment_id,
        title=asm.title,
        description=asm.description,
        created_at=asm.created_at.isoformat(),
        question_count=0,
        student_count=0,
        total_submissions=0,
    )


@app.get("/api/assessments", response_model=List[AssessmentSummaryResponse])
def list_assessments():
    assessments = repo.list_assessments()
    summaries = []
    for asm in assessments:
        total_subs = sum(len(q.submissions) for q in asm.questions.values())
        summaries.append(
            AssessmentSummaryResponse(
                assessment_id=asm.assessment_id,
                title=asm.title,
                description=asm.description,
                created_at=asm.created_at.isoformat(),
                question_count=len(asm.questions),
                student_count=len(asm.students),
                total_submissions=total_subs,
            )
        )
    return summaries


@app.post("/api/assessments/{assessment_id}/questions", response_model=QuestionSummaryResponse)
def create_question(assessment_id: str, req: CreateQuestionRequest):
    question = repo.add_question(assessment_id=assessment_id, title=req.title, description=req.description or "")
    if not question:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return QuestionSummaryResponse(
        question_id=question.question_id,
        assessment_id=question.assessment_id,
        title=question.title,
        description=question.description,
        submission_count=0,
        is_analyzed=False,
    )


@app.get("/api/assessments/{assessment_id}/questions", response_model=List[QuestionSummaryResponse])
def list_questions(assessment_id: str):
    asm = repo.get_assessment(assessment_id)
    if not asm:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return [
        QuestionSummaryResponse(
            question_id=q.question_id,
            assessment_id=q.assessment_id,
            title=q.title,
            description=q.description,
            submission_count=len(q.submissions),
            is_analyzed=q.last_analyzed_at is not None,
        )
        for q in asm.questions.values()
    ]


# --- Legacy Batch Analysis Route (Maintained for Backward Compatibility) ---

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

    # 1. Structural Plagiarism Detector
    results, boilerplate, boilerplate_spans = detector_engine.analyze_submissions(submissions)

    # 2. LLM Forensic Engine
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