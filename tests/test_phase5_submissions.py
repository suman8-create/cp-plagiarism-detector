# test_phase5_submissions.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_submission_pipeline():
    fib_solution = """#include <iostream>
using namespace std;
int fib(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
        int c = a + b;
        a = b;
        b = c;
    }
    return b;
}
int main() {
    int n;
    if (cin >> n) cout << fib(n) << endl;
    return 0;
}
"""
    # 1. Submit solution to Fibonacci problem
    res = client.post(
        "/api/problems/fibonacci-number/submit",
        json={
            "source_code": fib_solution,
            "user_id": "std_101",
            "user_name": "Alice Developer",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Accepted"
    assert data["submission_id"].startswith("sub_")
    assert data["passed_test_cases"] == data["total_test_cases"]
    print(f"[PASS] Solution submitted and recorded: ID {data['submission_id']}")

    # 2. Query problem submissions history
    history_res = client.get("/api/problems/fibonacci-number/submissions")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert history[0]["user_name"] == "Alice Developer"
    assert history[0]["status"] == "Accepted"
    print(f"[PASS] Submissions history retrieved: {len(history)} submission(s) found.")

if __name__ == "__main__":
    print("=== Running Phase 5 Submissions Pipeline Verification ===")
    test_submission_pipeline()
    print("All Phase 5 tests passed successfully!")