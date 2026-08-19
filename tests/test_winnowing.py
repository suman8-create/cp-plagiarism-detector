# test_winnowing.py
from engine.parser import CppNormalizer
from engine.fingerprint import WinnowingEngine

normalizer = CppNormalizer()
winnower = WinnowingEngine(k=6, w=4)

code = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += i;
    }
    cout << sum << endl;
    return 0;
}
"""

tokens = normalizer.normalize(code)
fingerprints = winnower.generate_fingerprints(tokens)

print(f"Total Tokens Extracted: {len(tokens)}")
print(f"Total Winnowed Fingerprints Generated: {len(fingerprints)}\n")

print(f"{'Hash Value (64-bit)':<22} | {'Line Span':<12}")
print("-" * 38)
for fp in fingerprints:
    print(f"{fp.hash_val:<22} | Line {fp.start_line} to {fp.end_line}")