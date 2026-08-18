# engine/repository.py

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from engine.models import (
    Contest,
    ContestParticipant,
    ExecutionResult,
    Problem,
    Submission,
    TestCase,
)


class AssessmentRepository:
    """
    Data store for Problems, Contests, Submissions, and Test Cases.
    """

    def __init__(self):
        self._problems: Dict[str, Problem] = {}
        self._submissions: Dict[str, Submission] = {}
        self._contests: Dict[str, Contest] = {}
        self._seed_default_problems()
        self._seed_default_contests()

    def _generate_slug(self, title: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title).strip().lower()
        return re.sub(r"[\s-]+", "-", slug)

    def _seed_default_problems(self):
        two_sum_starter = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

// Returns the 0-based indices of the two numbers that add up to target
vector<int> twoSum(const vector<int>& nums, int target) {
    // TODO: Write your solution here
    return {};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int n, target;
    if (!(cin >> n >> target)) return 0;
    
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }
    
    vector<int> result = twoSum(nums, target);
    if (!result.empty()) {
        cout << result[0] << " " << result[1] << endl;
    }
    return 0;
}
"""
        self.create_problem(
            title="Two Sum",
            description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
            difficulty="Easy",
            starter_code=two_sum_starter,
            constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "Exactly one valid answer exists."],
            examples=[
                {"input": "4 9\n2 7 11 15", "output": "0 1", "explanation": "nums[0] + nums[1] == 9, so return 0 1."}
            ],
            test_cases=[
                TestCase(input_data="4 9\n2 7 11 15", expected_output="0 1", is_sample=True, is_hidden=False),
                TestCase(input_data="3 6\n3 2 4", expected_output="1 2", is_sample=False, is_hidden=True),
                TestCase(input_data="2 6\n3 3", expected_output="0 1", is_sample=False, is_hidden=True),
            ],
        )

        fib_starter = """#include <iostream>
using namespace std;

// Calculates the nth Fibonacci number F(n)
int fibonacci(int n) {
    // TODO: Write your solution here
    return 0;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int n;
    if (cin >> n) {
        cout << fibonacci(n) << endl;
    }
    return 0;
}
"""
        self.create_problem(
            title="Fibonacci Number",
            description="The Fibonacci numbers, commonly denoted `F(n)`, form a sequence such that each number is the sum of the two preceding ones, starting from 0 and 1.\n\nGiven `n`, calculate `F(n)`.",
            difficulty="Easy",
            starter_code=fib_starter,
            constraints=["0 <= n <= 30"],
            examples=[
                {"input": "2", "output": "1", "explanation": "F(2) = F(1) + F(0) = 1 + 0 = 1."},
                {"input": "4", "output": "3", "explanation": "F(4) = F(3) + F(2) = 2 + 1 = 3."}
            ],
            test_cases=[
                TestCase(input_data="2", expected_output="1", is_sample=True, is_hidden=False),
                TestCase(input_data="4", expected_output="3", is_sample=True, is_hidden=False),
                TestCase(input_data="10", expected_output="55", is_sample=False, is_hidden=True),
                TestCase(input_data="0", expected_output="0", is_sample=False, is_hidden=True),
            ],
        )

    def _seed_default_contests(self):
        """Seeds initial contests: Live and Upcoming."""
        all_prob_ids = list(self._problems.keys())
        
        # 1. Live Contest
        live_contest = self.create_contest(
            title="Bi-Weekly Contest #1",
            description="Live competitive programming contest. Solve all algorithmic challenges within 90 minutes.",
            start_time=datetime.now(timezone.utc) - timedelta(minutes=15),
            duration_minutes=90,
            problem_ids=all_prob_ids,
        )
        self.register_contest_participant(live_contest.contest_id, "std_demo_101", "Alex Developer")

        # 2. Upcoming Contest
        self.create_contest(
            title="Grand Algorithms Championship",
            description="National coding speed challenge. Timed rating contest with full AST similarity auditing.",
            start_time=datetime.now(timezone.utc) + timedelta(hours=24),
            duration_minutes=120,
            problem_ids=all_prob_ids,
        )

    # --- Contest Operations ---

    def create_contest(
        self,
        title: str,
        description: str = "",
        start_time: Optional[datetime] = None,
        duration_minutes: int = 90,
        problem_ids: Optional[List[str]] = None,
    ) -> Contest:
        contest_id = f"cnt_{uuid.uuid4().hex[:8]}"
        start = start_time or datetime.now(timezone.utc)
        contest = Contest(
            contest_id=contest_id,
            title=title,
            description=description,
            start_time=start,
            duration_minutes=duration_minutes,
            problem_ids=problem_ids or list(self._problems.keys()),
        )
        self._contests[contest_id] = contest
        return contest

    def get_contest(self, contest_id: str) -> Optional[Contest]:
        return self._contests.get(contest_id)

    def list_contests(self) -> List[Contest]:
        return sorted(self._contests.values(), key=lambda c: c.start_time, reverse=True)

    def register_contest_participant(self, contest_id: str, user_id: str, user_name: str) -> Optional[ContestParticipant]:
        contest = self.get_contest(contest_id)
        if not contest:
            return None
        if user_id not in contest.participants:
            contest.participants[user_id] = ContestParticipant(user_id=user_id, user_name=user_name)
        return contest.participants[user_id]

    # --- Problem Operations ---

    def create_problem(
        self,
        title: str,
        description: str,
        difficulty: str = "Medium",
        starter_code: str = "",
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        test_cases: Optional[List[TestCase]] = None,
    ) -> Problem:
        problem_id = f"prob_{uuid.uuid4().hex[:8]}"
        slug = self._generate_slug(title)
        
        problem = Problem(
            problem_id=problem_id,
            title=title,
            slug=slug,
            description=description,
            difficulty=difficulty,
            starter_code=starter_code,
            constraints=constraints or [],
            examples=examples or [],
            test_cases=test_cases or [],
        )
        self._problems[problem_id] = problem
        return problem

    def get_problem(self, problem_id_or_slug: str) -> Optional[Problem]:
        if problem_id_or_slug in self._problems:
            return self._problems[problem_id_or_slug]
        for prob in self._problems.values():
            if prob.slug == problem_id_or_slug:
                return prob
        return None

    def list_problems(self) -> List[Problem]:
        return list(self._problems.values())

    # --- Submissions Operations ---

    def save_submission(
        self,
        problem_id: str,
        user_id: str,
        user_name: str,
        source_code: str,
        source_file: str = "solution.cpp",
        execution_result: Optional[ExecutionResult] = None,
        contest_id: Optional[str] = None,
    ) -> Submission:
        submission_id = f"sub_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        submission = Submission(
            submission_id=submission_id,
            problem_id=problem_id,
            user_id=user_id,
            user_name=user_name,
            source_file=source_file,
            source_code=source_code,
            contest_id=contest_id,
            execution_result=execution_result or ExecutionResult(),
            submitted_at=now,
        )

        self._submissions[submission_id] = submission

        problem = self.get_problem(problem_id)
        if problem:
            problem.submissions[submission_id] = submission

        if contest_id and contest_id in self._contests:
            contest = self._contests[contest_id]
            contest.submissions[submission_id] = submission

            if user_id not in contest.participants:
                contest.participants[user_id] = ContestParticipant(user_id=user_id, user_name=user_name)
            
            part = contest.participants[user_id]
            if execution_result and execution_result.status == "Accepted":
                if problem_id not in part.solved_problem_ids:
                    part.solved_problem_ids.append(problem_id)
                    part.score += 100
                    part.solved_timestamps[problem_id] = now.isoformat()
                    elapsed_min = max(0.0, (now - contest.start_time).total_seconds() / 60.0)
                    part.penalty_time_sec += elapsed_min * 60.0

        return submission

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        return self._submissions.get(submission_id)

    def get_problem_submissions(self, problem_id_or_slug: str) -> List[Submission]:
        problem = self.get_problem(problem_id_or_slug)
        if not problem:
            return []
        return sorted(problem.submissions.values(), key=lambda s: s.submitted_at, reverse=True)