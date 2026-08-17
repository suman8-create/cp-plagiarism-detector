# test_detector.py

from engine.detector import PlagiarismDetector

detector = PlagiarismDetector(k=6, w=4, boilerplate_threshold=0.50)

# Sample submissions
alice_code = """
#include <iostream>
#include <vector>
using namespace std;

void fast_io() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
}

int computeFib(int n) {
    if (n <= 1) return n;
    vector<int> dp(n + 1);
    dp[0] = 0;
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    return dp[n];
}

int main() {
    fast_io();
    int val;
    cin >> val;
    cout << computeFib(val) << endl;
    return 0;
}
"""

bob_code = """
#include <iostream>
#include <vector>
using namespace std;

void fast_io() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
}

int solve(int count) {
    if (count <= 1) return count;
    vector<int> memo(count + 1);
    memo[0] = 0;
    memo[1] = 1;
    for (int k = 2; k <= count; ++k) {
        memo[k] = memo[k - 1] + memo[k - 2];
    }
    return memo[count];
}

int main() {
    fast_io();
    int target;
    cin >> target;
    cout << solve(target) << endl;
    return 0;
}
"""

charlie_code = """
#include <iostream>
#include <vector>
using namespace std;

void fast_io() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
}

int fibonacci(int num) {
    int prev2 = 0, prev1 = 1;
    for (int step = 2; step <= num; step++) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return (num == 0) ? 0 : prev1;
}

int main() {
    fast_io();
    int query;
    cin >> query;
    cout << fibonacci(query) << endl;
    return 0;
}
"""

contest_submissions = {
    "alice.cpp": alice_code,
    "bob.cpp": bob_code,
    "charlie.cpp": charlie_code,
}

# Unpack all 3 return values
results, boilerplate, boilerplate_spans = detector.analyze_submissions(contest_submissions)

print(f"Total Shared Boilerplate Hashes Auto-Purged: {len(boilerplate)}")
print("\n--- Plagiarism Similarity Leaderboard ---")
for r in results:
    print(f"[{r.similarity_score}%] {r.file_a} vs {r.file_b} (Shared Hashes: {r.shared_fingerprints_count})")
    print(f"   Matched Spans A: {len(r.matched_lines_a)} segments")
    print(f"   Matched Spans B: {len(r.matched_lines_b)} segments")

print("\n--- Boilerplate Line Spans Detected ---")
for fname, spans in boilerplate_spans.items():
    print(f"   {fname}: {len(spans)} boilerplate line markers")