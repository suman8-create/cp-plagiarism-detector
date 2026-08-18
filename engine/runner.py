# engine/runner.py

import os
import shutil
import subprocess
import tempfile
import time
from typing import List
from engine.models import ExecutionResult, TestCase


class CppExecutionEngine:
    """
    Compiles and executes real C++ source code safely against problem test cases.
    Enforces static binary linking, execution timeouts, and strict output normalization.
    """

    def __init__(self, default_timeout_sec: float = 2.0):
        self.default_timeout_sec = default_timeout_sec
        
        # Candidate binary directories for MinGW / MSYS2 on Windows
        candidate_dirs = [
            r"C:\msys64\ucrt64\bin",
            r"C:\msys64\mingw64\bin",
            r"C:\MinGW\bin",
        ]
        
        # Build an enhanced PATH environment for child processes
        self.env = os.environ.copy()
        for cdir in candidate_dirs:
            if os.path.exists(cdir):
                self.env["PATH"] = cdir + os.pathsep + self.env.get("PATH", "")

        # Detect g++ or clang++
        self.compiler = shutil.which("g++", path=self.env["PATH"]) or shutil.which("clang++", path=self.env["PATH"])

    def _normalize_output(self, text: str) -> str:
        """Strips leading/trailing whitespace per line and normalizes line endings."""
        if not text:
            return ""
        lines = [line.strip() for line in text.strip().replace("\r\n", "\n").split("\n")]
        return "\n".join(lines)

    def execute(
        self,
        source_code: str,
        test_cases: List[TestCase],
        time_limit_sec: float = 2.0,
    ) -> ExecutionResult:
        if not test_cases:
            return ExecutionResult(
                status="Accepted",
                passed_test_cases=0,
                total_test_cases=0,
                stdout="No test cases configured.",
            )

        if not self.compiler:
            return ExecutionResult(
                status="Compilation Error",
                error_message="C++ compiler ('g++') was not found. Verify MSYS2/MinGW installation in PATH.",
                stderr="Missing compiler binary.",
            )

        # Create temporary execution workspace
        temp_dir = tempfile.mkdtemp(prefix="cp_exec_")
        source_path = os.path.join(temp_dir, "solution.cpp")
        binary_name = "solution.exe" if os.name == "nt" else "solution"
        binary_path = os.path.join(temp_dir, binary_name)

        try:
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(source_code)

            # Compile with C++17 and static runtime linking
            compile_cmd = [
                self.compiler,
                "-O2",
                "-std=c++17",
                "-static",
                "-static-libgcc",
                "-static-libstdc++",
                source_path,
                "-o",
                binary_path,
            ]

            try:
                compilation = subprocess.run(
                    compile_cmd,
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    env=self.env,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    status="Compilation Error",
                    error_message="Compilation timed out (> 10s).",
                )

            if compilation.returncode != 0:
                return ExecutionResult(
                    status="Compilation Error",
                    stderr=compilation.stderr,
                    error_message=f"Compilation failed: {compilation.stderr.strip()[:300]}",
                )

            passed_count = 0
            total_time_ms = 0.0
            last_stdout = ""

            # Run compiled binary against each test case individually
            for idx, tc in enumerate(test_cases):
                start_time = time.perf_counter()

                try:
                    input_payload = tc.input_data.strip() + "\n"
                    proc = subprocess.run(
                        [binary_path],
                        input=input_payload,
                        capture_output=True,
                        text=True,
                        timeout=time_limit_sec,
                        env=self.env,
                    )
                    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                    total_time_ms += elapsed_ms

                    if proc.returncode != 0:
                        return ExecutionResult(
                            status="Runtime Error",
                            passed_test_cases=passed_count,
                            total_test_cases=len(test_cases),
                            execution_time_ms=round(total_time_ms, 2),
                            stderr=proc.stderr,
                            error_message=f"Runtime error on test case {idx + 1} (Exit code {proc.returncode}).",
                        )

                    actual_clean = self._normalize_output(proc.stdout)
                    expected_clean = self._normalize_output(tc.expected_output)
                    last_stdout = actual_clean

                    if actual_clean == expected_clean:
                        passed_count += 1
                    else:
                        return ExecutionResult(
                            status="Wrong Answer",
                            passed_test_cases=passed_count,
                            total_test_cases=len(test_cases),
                            execution_time_ms=round(total_time_ms, 2),
                            stdout=actual_clean,
                            error_message=f"Failed on test case {idx + 1}. Expected '{expected_clean}' but got '{actual_clean}'.",
                        )

                except subprocess.TimeoutExpired:
                    return ExecutionResult(
                        status="Time Limit Exceeded",
                        passed_test_cases=passed_count,
                        total_test_cases=len(test_cases),
                        execution_time_ms=time_limit_sec * 1000.0,
                        error_message=f"Time limit of {time_limit_sec}s exceeded on test case {idx + 1}.",
                    )

            avg_time_ms = round(total_time_ms / max(len(test_cases), 1), 2)
            return ExecutionResult(
                status="Accepted",
                passed_test_cases=passed_count,
                total_test_cases=len(test_cases),
                execution_time_ms=avg_time_ms,
                stdout=last_stdout,
            )

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)