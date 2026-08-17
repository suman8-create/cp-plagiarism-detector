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