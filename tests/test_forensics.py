# test_forensics.py
from engine.forensics import LLMForensicEngine

engine = LLMForensicEngine()

# Sample 1: Typical ChatGPT Output with web artifacts, complexity note, and markdown artifact
ai_generated_code = """```cpp
#include <iostream>
#include <vector>
using namespace std;\u200B

// Function to calculate the nth Fibonacci number
int fibonacci(int n) {
    // Base case
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Time Complexity: O(2^n)
// Space Complexity: O(n)
int main() {
    // Driver code to test the function
    cout << fibonacci(5) << endl;
    return 0;
}
```"""

# Sample 2: Authentic Competitive Programmer Code
authentic_cp_code = """
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(0);
    cin.tie(0);
    int n;
    if (!(cin >> n)) return 0;
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        int c = a + b;
        a = b;
        b = c;
    }
    cout << a << "\n";
}
"""

print("=== Scanning AI-Generated Submission ===")
report_ai = engine.scan(ai_generated_code)
print(f"AI Confidence Score: {report_ai.ai_confidence_score}%")
print(f"Flagged Suspicious?: {report_ai.is_suspicious}")
print("Detected Red Flags:")
for flag in report_ai.flags:
    print(f"  * {flag}")

print("\n=== Scanning Authentic Human CP Submission ===")
report_human = engine.scan(authentic_cp_code)
print(f"AI Confidence Score: {report_human.ai_confidence_score}%")
print(f"Flagged Suspicious?: {report_human.is_suspicious}")
print(f"Detected Red Flags: {len(report_human.flags)}")