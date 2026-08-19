# test_phase2_problems.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_problem_endpoints():
    # 1. Fetch seeded problems
    res = client.get("/api/problems")
    assert res.status_code == 200
    problems = res.json()
    assert len(problems) >= 2
    
    slugs = [p["slug"] for p in problems]
    assert "two-sum" in slugs
    assert "fibonacci-number" in slugs
    print("[PASS] Seeded problem listing verified.")

    # 2. Fetch specific problem detail by slug
    detail_res = client.get("/api/problems/two-sum")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Two Sum"
    assert len(detail["sample_test_cases"]) > 0
    assert "#include <iostream>" in detail["starter_code"]
    print("[PASS] Problem detail & sample test cases verified.")

    # 3. Create a new custom problem
    new_prob = {
        "title": "Reverse Linked List",
        "description": "Reverse a singly linked list in-place.",
        "difficulty": "Easy",
        "starter_code": "/** Definition for singly-linked list. */",
        "constraints": ["The number of nodes in the list is the range [0, 5000]."],
        "examples": [{"input": "[1,2,3,4,5]", "output": "[5,4,3,2,1]"}],
        "test_cases": [
            {"input_data": "1 2 3", "expected_output": "3 2 1", "is_sample": True}
        ]
    }
    create_res = client.post("/api/problems", json=new_prob)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["slug"] == "reverse-linked-list"
    print("[PASS] Dynamic problem creation verified.")

if __name__ == "__main__":
    print("=== Running Phase 2 Problem System Verification ===")
    test_problem_endpoints()
    print("All problem tests passed successfully!")