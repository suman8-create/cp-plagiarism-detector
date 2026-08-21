# tests/test_single_integrity_audit.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_single_solution_integrity_report():
    # 1. Fetch available problems to obtain the exact active slug
    prob_list_res = client.get("/api/problems")
    assert prob_list_res.status_code == 200
    problems = prob_list_res.json()
    assert len(problems) > 0, "Problem library is empty."
    
    target_problem = next((p for p in problems if "two-sum" in p["slug"] or "two_sum" in p["slug"]), problems[0])
    target_slug = target_problem["slug"]
    print(f"[INFO] Running single integrity audit against problem: {target_slug}")

    alex_code = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> twoSum(const vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for(int i = 0; i < nums.size(); ++i) {
        int comp = target - nums[i];
        if(seen.count(comp)) return {seen[comp], i};
        seen[nums[i]] = i;
    }
    return {};
}

int main() {
    int n, target;
    if(cin >> n >> target) {
        vector<int> nums(n);
        for(int i = 0; i < n; ++i) cin >> nums[i];
        auto res = twoSum(nums, target);
        if(!res.empty()) cout << res[0] << " " << res[1] << endl;
    }
    return 0;
}"""

    # 1. Submit original solution as Alex
    res1 = client.post(
        f"/api/problems/{target_slug}/submit",
        json={
            "source_code": alex_code,
            "user_id": "std_alex_101",
            "user_name": "Alex Developer",
            "time_taken_seconds": 15.0,
        },
    )
    assert res1.status_code == 200, f"Alex submission failed with status {res1.status_code}: {res1.text}"
    assert res1.json()["status"] == "Accepted", f"Alex submission was not Accepted: {res1.json()}"
    print("[PASS] User A (Alex) submitted solution successfully.")

    # 2. Submit identical copied code as Suman
    res2 = client.post(
        f"/api/problems/{target_slug}/submit",
        json={
            "source_code": alex_code,
            "user_id": "std_suman_01",
            "user_name": "Suman",
            "time_taken_seconds": 8.0,
        },
    )
    assert res2.status_code == 200, f"Suman submission failed with status {res2.status_code}: {res2.text}"
    data2 = res2.json()
    assert "integrity_report" in data2, "Integrity report missing from submission response."
    
    rep = data2["integrity_report"]
    print(f"[PASS] User B Copied Submission Similarity: {rep['similarity_score']}%")
    print(f"[PASS] Matched Competitor: {rep['matched_user_name']}")
    print(f"[PASS] Verdict: {rep['verdict']}")
    print(f"[PASS] Flags: {rep['forensic_flags']}")

    assert rep["similarity_score"] >= 80.0
    assert rep["verdict"] in ("Plagiarized", "Suspicious Similarity")
    assert rep["matched_user_name"] == "Alex Developer"
    print("[ALL SINGLE INTEGRITY AUDIT CHECKS PASSED]")


if __name__ == "__main__":
    test_single_solution_integrity_report()