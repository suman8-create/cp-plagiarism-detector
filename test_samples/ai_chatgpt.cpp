// test_samples/ai_chatgpt.cpp
#include <iostream>
#include <vector>
using namespace std;

// Function to calculate the factorial of a number
int factorial(int n) {
    // Base case
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Time Complexity: O(n)
// Space Complexity: O(n)
int main() {
    // Driver code to test the function
    cout << factorial(5) << endl;
    return 0;
}