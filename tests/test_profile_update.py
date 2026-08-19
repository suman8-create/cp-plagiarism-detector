# tests/test_profile_update.py

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_profile_update_after_submission():
    # 1. Submit accepted solution for Two Sum
    sol_code = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;
vector<int> twoSum(const vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for(int i=0; i<nums.size(); ++i) {
        int comp = target - nums[i];
        if(seen.count(comp)) return {seen[comp], i};
        seen[nums[i]] = i;
    }
    return {};
}
int main(){
    int n, target;
    if(cin >> n >> target){
        vector<int> nums(n);
        for(int i=0; i<n; ++i) cin >> nums[i];
        auto res = twoSum(nums, target);
        if(!res.empty()) cout << res[0] << " " << res[1] << endl;
    }
    return 0;
}"""

    sub_res = client.post(
        "/api/problems/two-sum/submit",
        json={
            "source_code": sol_code,
            "user_id": "std_suman_01",
            "user_name": "Suman",
            "time_taken_seconds": 45.0
        }
    )
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "Accepted"
    print("[PASS] Submission accepted successfully.")

    # 2. Query Profile endpoint
    prof_res = client.get("/api/users/std_suman_01/profile?user_name=Suman&handle=%40suman")
    assert prof_res.status_code == 200, f"Profile endpoint failed: {prof_res.text}"
    profile = prof_res.json()

    print(f"[PASS] Total Solved: {profile['total_solved']}")
    print(f"[PASS] Total Submissions: {profile['total_submissions']}")
    print(f"[PASS] Accuracy: {profile['accuracy_percentage']}%")
    print(f"[PASS] Skills Breakdown: {profile['skills_breakdown']}")
    
    assert profile["total_solved"] >= 1
    assert profile["total_submissions"] >= 1
    assert "Array" in profile["skills_breakdown"]
    assert "Hash Table" in profile["skills_breakdown"]
    print("[ALL CHECKS PASSED] Profile accurately updated with submissions and skill tags!")

if __name__ == "__main__":
    test_profile_update_after_submission()