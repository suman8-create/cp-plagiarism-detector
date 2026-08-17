# test_detector.py
from engine.detector import PlagiarismDetector

# Standard CP Template used by all 4 students
CP_TEMPLATE = """
#include <iostream>
#include <vector>
using namespace std;

void fast_io() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
}
"""

# Alice: Original DP Solution
alice_code = CP_TEMPLATE + """
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
    int n;
    cin >> n;
    cout << computeFib(n) << endl;
    return 0;
}
"""

# Bob: Blatant copy of Alice, renamed vars and disguised formatting
bob_code = CP_TEMPLATE + """
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
    int val;
    cin >> val;
    cout << solve(val) << endl;
    return 0;
}
"""

# Charlie: Honest student, completely different logic (Iterative Space-Optimized)
charlie_code = CP_TEMPLATE + """
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

# David: Solved a different graph problem
david_code = CP_TEMPLATE + """
void bfs(int src, vector<vector<int>>& adj) {
    vector<bool> visited(adj.size(), false);
    vector<int> q;
    visited[src] = true;
    q.push_back(src);
    int head = 0;
    while (head < q.size()) {
        int u = q[head++];
        for (int v : adj[u]) {
            if (!visited[v]) {
                visited[v] = true;
                q.push_back(v);
            }
        }
    }
}

int main() {
    fast_io();
    return 0;
}
"""

contest_submissions = {
    "alice.cpp": alice_code,
    "bob.cpp": bob_code,
    "charlie.cpp": charlie_code,
    "david.cpp": david_code,
}

# Run detector
detector = PlagiarismDetector()
results, boilerplate = detector.analyze_submissions(contest_submissions)

print(f"Learned & Filtered Boilerplate Hashes: {len(boilerplate)}")
print("\n" + "=" * 60)
print(f"{'Pair':<25} | {'Similarity Score':<18} | {'Shared Hashes'}")
print("=" * 60)

for res in results:
    pair_label = f"{res.file_a} vs {res.file_b}"
    print(f"{pair_label:<25} | {res.similarity_score:>6.2f}%            | {res.shared_fingerprints_count}")