# engine/repository.py

import uuid
from typing import Dict, List, Optional
from engine.models import Assessment, Question, Student, Submission


class AssessmentRepository:
    """
    In-memory data store for assessments, questions, students, and submissions.
    Designed with repository-pattern interfaces so it can easily swap to SQLite/Postgres.
    """

    def __init__(self):
        self._assessments: Dict[str, Assessment] = {}

    def create_assessment(self, title: str, description: str = "") -> Assessment:
        assessment_id = f"asm_{uuid.uuid4().hex[:8]}"
        assessment = Assessment(
            assessment_id=assessment_id,
            title=title,
            description=description,
        )
        self._assessments[assessment_id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str) -> Optional[Assessment]:
        return self._assessments.get(assessment_id)

    def list_assessments(self) -> List[Assessment]:
        return list(self._assessments.values())

    def add_question(self, assessment_id: str, title: str, description: str = "") -> Optional[Question]:
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return None

        question_id = f"q_{uuid.uuid4().hex[:8]}"
        question = Question(
            question_id=question_id,
            assessment_id=assessment_id,
            title=title,
            description=description,
        )
        assessment.questions[question_id] = question
        return question

    def get_question(self, assessment_id: str, question_id: str) -> Optional[Question]:
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return None
        return assessment.questions.get(question_id)

    def add_submission(
        self,
        assessment_id: str,
        question_id: str,
        student_id: str,
        student_name: str,
        source_file: str,
        source_code: str,
    ) -> Optional[Submission]:
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return None

        question = assessment.questions.get(question_id)
        if not question:
            return None

        submission_id = f"sub_{uuid.uuid4().hex[:8]}"
        submission = Submission(
            submission_id=submission_id,
            assessment_id=assessment_id,
            question_id=question_id,
            student_id=student_id,
            student_name=student_name,
            source_file=source_file,
            source_code=source_code,
        )

        question.submissions[submission_id] = submission

        # Track or update student entity in assessment
        if student_id not in assessment.students:
            assessment.students[student_id] = Student(student_id=student_id, name=student_name)
        assessment.students[student_id].submission_ids.append(submission_id)

        return submission