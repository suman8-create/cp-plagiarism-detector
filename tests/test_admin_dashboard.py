# tests/test_admin_dashboard.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_admin_dashboard_workflow():
    # 1. Test Admin Login
    login_res = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    admin_info = login_res.json()
    assert admin_info["role"] == "admin"
    print("[PASS] Admin authenticated successfully.")

    # 2. Test Fetch Admin Contests
    contests_res = client.get("/api/admin/contests")
    assert contests_res.status_code == 200
    contests = contests_res.json()
    assert len(contests) > 0
    contest_id = contests[0]["contest_id"]
    print(f"[PASS] Fetched {len(contests)} contests for Admin Review.")

    # 3. Test Audit Report Matrix for Admin
    audit_res = client.get(f"/api/contests/{contest_id}/audit")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert "similarity_matrices" in audit_data
    assert "suspect_pairs" in audit_data
    print(f"[PASS] Audit Matrices & Suspect Queue loaded for {contest_id}.")
    print("[ALL ADMIN DASHBOARD WORKFLOW CHECKS PASSED]")

if __name__ == "__main__":
    test_admin_dashboard_workflow()