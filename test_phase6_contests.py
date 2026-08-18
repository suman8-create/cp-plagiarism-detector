# test_phase6_contests.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_contest_lifecycle():
    # 1. Fetch seeded active contest
    res = client.get("/api/contests")
    assert res.status_code == 200
    contests = res.json()
    assert len(contests) >= 1
    default_contest = contests[0]
    assert default_contest["status"] == "ACTIVE"
    assert default_contest["title"] == "Weekly CodeSprint #1"
    print(f"[PASS] Seeded contest verified: {default_contest['title']} (Status: {default_contest['status']})")

    # 2. Fetch contest detail with problem set
    detail_res = client.get(f"/api/contests/{default_contest['contest_id']}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["problems"]) >= 2
    print(f"[PASS] Contest problem set loaded: {len(detail['problems'])} problems.")

    # 3. Create a new custom contest
    new_contest_payload = {
        "title": "Algorithms Championship 2026",
        "description": "Final championship round.",
        "start_time_offset_min": 60,  # Starts in 1 hour (UPCOMING)
        "duration_minutes": 120,
    }
    create_res = client.post("/api/contests", json=new_contest_payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["status"] == "UPCOMING"
    assert created["duration_minutes"] == 120
    print(f"[PASS] Future contest created successfully (Status: {created['status']}).")

    # 4. Register a participant
    reg_res = client.post(
        f"/api/contests/{default_contest['contest_id']}/register",
        params={"user_id": "usr_999", "user_name": "Champion Coder"}
    )
    assert reg_res.status_code == 200
    print("[PASS] Participant registered to contest.")

if __name__ == "__main__":
    print("=== Running Phase 6 Timed Contest Verification ===")
    test_contest_lifecycle()
    print("All Phase 6 tests passed successfully!")