# test_phase1_models.py

from fastapi.testclient import TestClient
from api.main import app
from engine.repository import AssessmentRepository

client = TestClient(app)

def test_domain_repository():
    repo = AssessmentRepository()
    
    # 1. Create Assessment
    asm = repo.create_assessment(title="DSA Midterm Exam 2026", description="Practical assessment")
    assert asm.assessment_id.startswith("asm_")
    assert asm.title == "DSA Midterm Exam 2026"
    
    # 2. Add Questions
    q1 = repo.add_question(asm.assessment_id, title="Fibonacci DP", description="Compute nth Fibonacci")
    q2 = repo.add_question(asm.assessment_id, title="Dijkstra Shortest Path", description="Graph traversal")
    assert len(asm.questions) == 2
    
    # 3. Add Submissions
    sub1 = repo.add_submission(
        assessment_id=asm.assessment_id,
        question_id=q1.question_id,
        student_id="std_101",
        student_name="Alice",
        source_file="alice_fib.cpp",
        source_code="int main() { return 0; }",
    )
    assert sub1.student_name == "Alice"
    assert len(asm.students) == 1
    assert "std_101" in asm.students
    print("[PASS] Domain repository unit test passed.")


def test_assessment_endpoints():
    # 1. Create assessment via REST API
    res = client.post("/api/assessments", json={"title": "Algorithms Lab Final", "description": "Semester 4 Final"})
    assert res.status_code == 200
    asm_data = res.json()
    asm_id = asm_data["assessment_id"]
    assert asm_data["title"] == "Algorithms Lab Final"

    # 2. Create question in assessment
    q_res = client.post(f"/api/assessments/{asm_id}/questions", json={"title": "0/1 Knapsack Problem"})
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["title"] == "0/1 Knapsack Problem"

    # 3. List assessments
    list_res = client.get("/api/assessments")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Verify backward compatibility of legacy upload endpoint
    legacy_files = [
        ("files", ("alice.cpp", b"#include <iostream>\nint main(){ return 0; }", "text/plain")),
        ("files", ("bob.cpp", b"#include <iostream>\nint main(){ return 0; }", "text/plain")),
    ]
    check_res = client.post("/api/check-plagiarism", files=legacy_files)
    assert check_res.status_code == 200
    assert check_res.json()["total_files_analyzed"] == 2
    print("[PASS] API assessment & backward-compatibility tests passed.")


if __name__ == "__main__":
    test_domain_repository()
    test_assessment_endpoints()