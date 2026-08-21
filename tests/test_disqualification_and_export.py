# tests/test_disqualification_and_export.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_disqualification_and_audit_export():
    # 1. Fetch available contests
    contests_res = client.get("/api/contests")
    assert contests_res.status_code == 200
    contests = contests_res.json()
    assert len(contests) > 0
    contest_id = contests[0]["contest_id"]

    # 2. Run Audit to ensure suspect pairs exist
    audit_res = client.post(f"/api/contests/{contest_id}/audit")
    assert audit_res.status_code == 200
    report = audit_res.json()
    assert len(report["suspect_pairs"]) > 0, "No suspect pairs available to test disqualification."

    target_pair = report["suspect_pairs"][0]
    bad_user_id = target_pair["user_a_id"]
    partner_id = target_pair["user_b_id"]
    problem_id = target_pair["problem_id"]
    print(f"[INFO] Testing Disqualification on: {target_pair['user_a_name']} ({bad_user_id})")

    # 3. Disqualify User A
    dec_res = client.post(
        "/api/admin/contests/decision",
        json={
            "contest_id": contest_id,
            "problem_id": problem_id,
            "user_id": bad_user_id,
            "partner_user_id": partner_id,
            "action": "DISQUALIFIED",
            "reason": "Confirmed unauthorized code exchange during live contest window."
        }
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["action_recorded"] == "DISQUALIFIED"
    print("[PASS] Admin decision recorded successfully.")

    # 4. Check Leaderboard Standings to ensure participant is reranked/disqualified
    board_res = client.get(f"/api/contests/{contest_id}/leaderboard")
    assert board_res.status_code == 200
    board_data = board_res.json()
    rows = board_data.get("rows") or board_data.get("rankings") or []
    
    dq_user = next((p for p in rows if p["user_id"] == bad_user_id), None)
    assert dq_user is not None, f"User {bad_user_id} not found in leaderboard."
    assert dq_user["disqualified"] is True
    assert dq_user["score"] == 0
    print(f"[PASS] Participant {dq_user['user_name']} score reset to 0 with Disqualified status.")

    # 5. Test CSV Export Endpoint
    csv_res = client.get(f"/api/admin/contests/{contest_id}/export/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers.get("content-type", "")
    assert "AST Similarity" in csv_res.text
    print("[PASS] Forensic Audit CSV generated and exported successfully.")
    print("[ALL DISQUALIFICATION & AUDIT EXPORT CHECKS PASSED]")


if __name__ == "__main__":
    test_disqualification_and_audit_export()