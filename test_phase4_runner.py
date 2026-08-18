# test_phase4_runner.py

from fastapi.testclient import TestClient
from api.main import app
from engine.runner import CppExecutionEngine
from engine.models import TestCase

client = TestClient(app)

def test_execution_engine_verdicts():
    runner = CppExecutionEngine()
    
    # 1. Test Accepted Solution
    good_code = """#include <iostream>
using namespace std;
int main() {
    int a, b;
    if (cin >> a >> b) {
        cout << (a + b) << endl;
    }
    return 0;
}
"""
    test_cases = [
        TestCase(input_data="2 3", expected_output="5"),
        TestCase(input_data="10 20", expected_output="30"),
    ]
    res_ac = runner.execute(good_code, test_cases)
    
    print(f"DEBUG res_ac.status: {res_ac.status}")
    print(f"DEBUG res_ac.error_message: {res_ac.error_message}")
    print(f"DEBUG res_ac.stderr: {res_ac.stderr}")
    print(f"DEBUG res_ac.stdout: {res_ac.stdout}")
    
    assert res_ac.status == "Accepted", f"Expected 'Accepted' but got '{res_ac.status}' (Error: {res_ac.error_message}, stderr: {res_ac.stderr})"
    assert res_ac.passed_test_cases == 2
    print("[PASS] Execution: 'Accepted' verdict verified.")

    # 2. Test Wrong Answer Solution
    wrong_code = """#include <iostream>
using namespace std;
int main() {
    int a, b;
    if (cin >> a >> b) {
        cout << (a * b) << endl;
    }
    return 0;
}
"""
    res_wa = runner.execute(wrong_code, test_cases)
    assert res_wa.status == "Wrong Answer"
    assert res_wa.passed_test_cases == 0
    print("[PASS] Execution: 'Wrong Answer' verdict verified.")

    # 3. Test Compilation Error
    broken_code = """#include <iostream>
int main() {
    invalid_syntax_error();
    return 0;
}
"""
    res_ce = runner.execute(broken_code, test_cases)
    assert res_ce.status == "Compilation Error"
    print("[PASS] Execution: 'Compilation Error' verdict verified.")

    # 4. Test Time Limit Exceeded
    tle_code = """#include <iostream>
int main() {
    while (true) {}
    return 0;
}
"""
    res_tle = runner.execute(tle_code, test_cases, time_limit_sec=0.5)
    assert res_tle.status == "Time Limit Exceeded"
    print("[PASS] Execution: 'Time Limit Exceeded' verdict verified.")


def test_execution_api_endpoint():
    fib_solution = """#include <iostream>
using namespace std;
int fib(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
        int c = a + b;
        a = b;
        b = c;
    }
    return b;
}
int main() {
    int n;
    if (cin >> n) cout << fib(n) << endl;
    return 0;
}
"""
    res = client.post("/api/problems/fibonacci-number/run", json={"source_code": fib_solution})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Accepted", f"API /run returned {data}"
    print("[PASS] API '/run' endpoint verified.")


if __name__ == "__main__":
    print("=== Running Phase 4 Execution Engine Verification ===")
    test_execution_engine_verdicts()
    test_execution_api_endpoint()
    print("All Execution Engine tests passed successfully!")