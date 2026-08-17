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
    int val;
    cin >> val;
    cout << solve(val) << endl;
    return 0;
}