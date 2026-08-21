# tests/test_contest_audit_batch.py

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_contest_batch_plagiarism_audit():
    # 1. Fetch available contest
    contests_res = client.get("/api/contests")
    assert contests_res.status_code == 200
    contests = contests_res.json()
    assert len(contests) > 0, "No contests found."
    contest_id = contests[0]["contest_id"]
    print(f"[INFO] Running contest batch audit on: {contest_id}")

    # 2. Submit solution as Competitor 1 (Alex)
    two_sum_code = """#include <iostream>
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

    client.post(
        "/api/problems/two-sum/submit",
        json={
            "source_code": two_sum_code,
            "user_id": "std_alex_101",
            "user_name": "Alex Developer",
            "contest_id": contest_id,
            "time_taken_seconds": 40.0,
        },
    )

    # 3. Submit identical solution as Competitor 2 (Priya) within 60 seconds
    client.post(
        "/api/problems/two-sum/submit",
        json={
            "source_code": two_sum_code,
            "user_id": "std_priya_202",
            "user_name": "Priya Sharma",
            "contest_id": contest_id,
            "time_taken_seconds": 45.0,
        },
    )

    # 4. Trigger automated contest batch audit
    audit_res = client.post(f"/api/contests/{contest_id}/audit")
    assert audit_res.status_code == 200, f"Audit failed: {audit_res.text}"
    report = audit_res.json()

    print(f"[PASS] Total Submissions Audited: {report['total_submissions_audited']}")
    print(f"[PASS] Flagged Suspect Pairs: {report['flagged_pairs_count']}")
    assert report["flagged_pairs_count"] >= 1

    top_pair = report["suspect_pairs"][0]
    print(f"[PASS] Pair: {top_pair['user_a_name']} <-> {top_pair['user_b_name']}")
    print(f"[PASS] AST Similarity: {top_pair['ast_similarity']}%")
    print(f"[PASS] Suspicion Score: {top_pair['suspicion_score']}")
    print(f"[PASS] Flags: {top_pair['flags']}")

    assert top_pair["ast_similarity"] >= 90.0
    assert top_pair["suspicion_score"] >= 90.0
    print("[ALL CONTEST BATCH AUDIT CHECKS PASSED]")


if __name__ == "__main__":
    test_contest_batch_plagiarism_audit()