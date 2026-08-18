# test_phase7_leaderboard.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_leaderboard_scoring():
    # 1. Fetch live contest
    contests_res = client.get("/api/contests")
    assert contests_res.status_code == 200
    live_c = [c for c in contests_res.json() if c["status"] == "Live"][0]
    cid = live_c["contest_id"]
    print(f"[PASS] Testing Leaderboard on live contest: {live_c['title']}")

    # 2. Fetch Leaderboard
    board_res = client.get(f"/api/contests/{cid}/leaderboard")
    assert board_res.status_code == 200
    board = board_res.json()
    assert "standings" in board
    assert len(board["standings"]) >= 2
    
    # Verify Rank 1 participant has highest score / lowest penalty
    rank_1 = board["standings"][0]
    assert rank_1["rank"] == 1
    assert rank_1["score"] >= 100
    print(f"[PASS] Rank 1 Competitor: {rank_1['user_name']} (Score: {rank_1['score']} pts, Penalty: {rank_1['total_penalty_min']}m)")

    # 3. Register a new user and submit an AC solution
    reg_res = client.post(f"/api/contests/{cid}/register", params={"user_id": "std_suman_01", "user_name": "Suman"})
    assert reg_res.status_code == 200

    two_sum_sol = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;
vector<int> twoSum(const vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < nums.size(); ++i) {
        int comp = target - nums[i];
        if (seen.count(comp)) return {seen[comp], i};
        seen[nums[i]] = i;
    }
    return {};
}
int main() {
    int n, target;
    if (cin >> n >> target) {
        vector<int> nums(n);
        for (int i = 0; i < n; ++i) cin >> nums[i];
        vector<int> res = twoSum(nums, target);
        if (!res.empty()) cout << res[0] << " " << res[1] << endl;
    }
    return 0;
}
"""
    sub_res = client.post(
        "/api/problems/two-sum/submit",
        json={
            "source_code": two_sum_sol,
            "user_id": "std_suman_01",
            "user_name": "Suman",
            "contest_id": cid,
        },
    )
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "Accepted"

    # 4. Verify Leaderboard updated with Suman's score
    updated_board = client.get(f"/api/contests/{cid}/leaderboard").json()
    suman_row = [r for r in updated_board["standings"] if r["user_id"] == "std_suman_01"][0]
    assert suman_row["score"] == 100
    assert suman_row["problems_solved"] >= 1
    print(f"[PASS] Verified Suman dynamically scored and placed on leaderboard (Rank {suman_row['rank']})")

if __name__ == "__main__":
    print("=== Running Phase 7 Leaderboard Engine Verification ===")
    test_leaderboard_scoring()
    print("All Phase 7 tests passed successfully!")