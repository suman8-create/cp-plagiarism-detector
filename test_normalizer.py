# test_normalizer.py
from engine.parser import CppNormalizer

normalizer = CppNormalizer()

# Submission 1: Original solution
code_a = """
// Original author
#include <iostream>

int calculateSum(int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += i;
    }
    return total;
}
"""

# Submission 2: Disguised copy (renamed variables, removed comments, different formatting)
code_b = """
#include <iostream>
int foo(int limit){
int ans=0;
for(int idx=0;idx<limit;idx++){ans+=idx;}
return ans;}
"""

tokens_a = normalizer.normalize(code_a)
tokens_b = normalizer.normalize(code_b)

stream_a = [t.value for t in tokens_a]
stream_b = [t.value for t in tokens_b]

print("=== Normalized Stream A ===")
print(" ".join(stream_a))

print("\n=== Normalized Stream B ===")
print(" ".join(stream_b))

print("\nAre the normalized token streams identical?:", stream_a == stream_b)