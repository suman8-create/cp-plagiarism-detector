# engine/repository.py

import hashlib
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from engine.models import (
    Contest,
    ContestLeaderboardResponse,
    ContestParticipant,
    ContestStatus,
    ExecutionResult,
    LeaderboardProblemCell,
    LeaderboardRow,
    Problem,
    ProblemSummaryResponse,
    Submission,
    TestCase,
    UserProfileStats,
)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "platform_data.db")


def json_dump_helper(data) -> str:
    """Helper to safely dump dicts containing datetimes and Pydantic models."""
    return json.dumps(data, default=str)


class AssessmentRepository:
    def __init__(self):
        self._init_db()
        self._seed_default_problems()
        self._seed_default_contests()

    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _hash_pw(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS problems (
                    problem_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    category TEXT,
                    topic_tags TEXT,
                    description TEXT,
                    difficulty TEXT,
                    time_limit_sec REAL,
                    memory_limit_mb INTEGER,
                    starter_code TEXT,
                    constraints TEXT,
                    examples TEXT,
                    test_cases TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    submission_id TEXT PRIMARY KEY,
                    problem_id TEXT NOT NULL,
                    problem_title TEXT,
                    user_id TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    source_file TEXT,
                    source_code TEXT,
                    contest_id TEXT,
                    time_taken_seconds REAL,
                    execution_result TEXT,
                    submitted_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contests (
                    contest_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT,
                    duration_minutes INTEGER,
                    problem_ids TEXT,
                    participants TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()

    def _generate_slug(self, title: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title).strip().lower()
        return re.sub(r"[\s-]+", "-", slug)

    # --- User Authentication Operations ---

    def register_user(self, username: str, display_name: str, password: str) -> Dict:
        username_clean = username.strip().lower().replace("@", "")
        with self._get_conn() as conn:
            existing = conn.execute("SELECT * FROM users WHERE username = ?", (username_clean,)).fetchone()
            if existing:
                raise ValueError("Username already taken. Please choose another.")

            user_id = f"usr_{uuid.uuid4().hex[:8]}"
            now = datetime.now(timezone.utc).isoformat()
            pw_hash = self._hash_pw(password)

            conn.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                (user_id, username_clean, display_name.strip(), pw_hash, now),
            )
            conn.commit()

            return {
                "user_id": user_id,
                "username": f"@{username_clean}",
                "display_name": display_name.strip(),
            }

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        username_clean = username.strip().lower().replace("@", "")
        pw_hash = self._hash_pw(password)
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username_clean, pw_hash),
            ).fetchone()
            if not row:
                return None
            return {
                "user_id": row["user_id"],
                "username": f"@{row['username']}",
                "display_name": row["display_name"],
            }

    # --- Default Seeding ---

    def _seed_default_problems(self):
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()["c"]
            if count > 0:
                return

        two_sum_starter = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> twoSum(const vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < nums.size(); ++i) {
        int comp = target - nums[i];
        if (seen.count(comp)) return {seen[comp], i};
        seen[nums[i]] = i;
    }
    return {};
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int n, target;
    if (!(cin >> n >> target)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) cin >> nums[i];
    vector<int> result = twoSum(nums, target);
    if (!result.empty()) cout << result[0] << " " << result[1] << endl;
    return 0;
}
"""
        self.create_problem(
            title="Two Sum",
            category="Algorithms",
            topic_tags=["Array", "Hash Table"],
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

int fibonacci(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
        int c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int n;
    if (cin >> n) cout << fibonacci(n) << endl;
    return 0;
}
"""
        self.create_problem(
            title="Fibonacci Number",
            category="Algorithms",
            topic_tags=["Math", "Dynamic Programming"],
            description="The Fibonacci numbers form a sequence where each number is the sum of the two preceding ones, starting from 0 and 1.\n\nGiven `n`, calculate `F(n)`.",
            difficulty="Easy",
            starter_code=fib_starter,
            constraints=["0 <= n <= 30"],
            examples=[
                {"input": "2", "output": "1", "explanation": "F(2) = 1."},
                {"input": "4", "output": "3", "explanation": "F(4) = 3."}
            ],
            test_cases=[
                TestCase(input_data="2", expected_output="1", is_sample=True, is_hidden=False),
                TestCase(input_data="4", expected_output="3", is_sample=True, is_hidden=False),
                TestCase(input_data="10", expected_output="55", is_sample=False, is_hidden=True),
                TestCase(input_data="0", expected_output="0", is_sample=False, is_hidden=True),
            ],
        )

        add_two_num = """#include <iostream>
using namespace std;

int main() {
    long long a, b;
    if (cin >> a >> b) {
        cout << (a + b) << endl;
    }
    return 0;
}
"""
        self.create_problem(
            title="Add Two Numbers",
            category="Algorithms",
            topic_tags=["Math", "Simulation"],
            description="Given two integers `a` and `b`, output their sum.",
            difficulty="Medium",
            starter_code=add_two_num,
            constraints=["-10^18 <= a, b <= 10^18"],
            examples=[{"input": "12 28", "output": "40", "explanation": "12 + 28 = 40"}],
            test_cases=[
                TestCase(input_data="12 28", expected_output="40", is_sample=True, is_hidden=False),
                TestCase(input_data="-5 15", expected_output="10", is_sample=False, is_hidden=True),
            ],
        )

    def _seed_default_contests(self):
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) as c FROM contests").fetchone()["c"]
            if count > 0:
                return

        all_prob_ids = [p.problem_id for p in self.list_problems()]
        p_two_sum = all_prob_ids[0]
        p_fib = all_prob_ids[1] if len(all_prob_ids) > 1 else all_prob_ids[0]
        
        live_contest = self.create_contest(
            title="Bi-Weekly Contest #1",
            description="Live competitive programming contest. Solve algorithmic challenges within 90 minutes.",
            start_time=datetime.now(timezone.utc) - timedelta(minutes=20),
            duration_minutes=90,
            problem_ids=all_prob_ids,
        )

        self.register_contest_participant(live_contest.contest_id, "std_alex_101", "Alex Developer")
        self.save_submission(
            problem_id=p_fib,
            user_id="std_alex_101",
            user_name="Alex Developer",
            source_code="// Alex Fibonacci",
            time_taken_seconds=180.0,
            execution_result=ExecutionResult(status="Accepted", passed_test_cases=4, total_test_cases=4, execution_time_ms=12.4, memory_mb=42.1),
            contest_id=live_contest.contest_id,
        )

        self.register_contest_participant(live_contest.contest_id, "std_priya_202", "Priya Sharma")
        self.save_submission(
            problem_id=p_two_sum,
            user_id="std_priya_202",
            user_name="Priya Sharma",
            source_code="// Priya TwoSum",
            time_taken_seconds=320.0,
            execution_result=ExecutionResult(status="Accepted", passed_test_cases=3, total_test_cases=3, execution_time_ms=18.5, memory_mb=44.6),
            contest_id=live_contest.contest_id,
        )

        self.create_contest(
            title="Grand Algorithms Championship",
            description="National coding challenge with AST similarity auditing.",
            start_time=datetime.now(timezone.utc) + timedelta(hours=24),
            duration_minutes=120,
            problem_ids=all_prob_ids,
        )

    # --- Problem Operations ---

    def create_problem(
        self,
        title: str,
        description: str,
        difficulty: str = "Medium",
        category: str = "Algorithms",
        topic_tags: Optional[List[str]] = None,
        starter_code: str = "",
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        test_cases: Optional[List[TestCase]] = None,
    ) -> Problem:
        problem_id = f"prob_{uuid.uuid4().hex[:8]}"
        slug = self._generate_slug(title)
        now = datetime.now(timezone.utc).isoformat()
        
        tc_data = [tc.model_dump() for tc in (test_cases or [])]

        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO problems VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    problem_id,
                    title,
                    slug,
                    category,
                    json_dump_helper(topic_tags or []),
                    description,
                    difficulty,
                    2.0,
                    256,
                    starter_code,
                    json_dump_helper(constraints or []),
                    json_dump_helper(examples or []),
                    json_dump_helper(tc_data),
                    now,
                ),
            )
            conn.commit()

        return self.get_problem(problem_id)

    def get_problem(self, problem_id_or_slug: str) -> Optional[Problem]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM problems WHERE problem_id = ? OR slug = ?",
                (problem_id_or_slug, problem_id_or_slug),
            ).fetchone()
            if not row:
                return None
            return Problem(
                problem_id=row["problem_id"],
                title=row["title"],
                slug=row["slug"],
                category=row["category"] or "Algorithms",
                topic_tags=json.loads(row["topic_tags"] or "[]"),
                description=row["description"],
                difficulty=row["difficulty"],
                time_limit_sec=row["time_limit_sec"],
                memory_limit_mb=row["memory_limit_mb"],
                starter_code=row["starter_code"],
                constraints=json.loads(row["constraints"] or "[]"),
                examples=json.loads(row["examples"] or "[]"),
                test_cases=[TestCase(**tc) for tc in json.loads(row["test_cases"] or "[]")],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_problems(self) -> List[Problem]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM problems ORDER BY rowid ASC").fetchall()
            return [
                Problem(
                    problem_id=r["problem_id"],
                    title=r["title"],
                    slug=r["slug"],
                    category=r["category"] or "Algorithms",
                    topic_tags=json.loads(r["topic_tags"] or "[]"),
                    description=r["description"],
                    difficulty=r["difficulty"],
                    time_limit_sec=r["time_limit_sec"],
                    memory_limit_mb=r["memory_limit_mb"],
                    starter_code=r["starter_code"],
                    constraints=json.loads(r["constraints"] or "[]"),
                    examples=json.loads(r["examples"] or "[]"),
                    test_cases=[TestCase(**tc) for tc in json.loads(r["test_cases"] or "[]")],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]

    # --- Submissions Operations ---

    def save_submission(
        self,
        problem_id: str,
        user_id: str,
        user_name: str,
        source_code: str,
        source_file: str = "solution.cpp",
        time_taken_seconds: float = 0.0,
        execution_result: Optional[ExecutionResult] = None,
        contest_id: Optional[str] = None,
    ) -> Submission:
        submission_id = f"sub_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        resolved_prob = self.get_problem(problem_id)
        canonical_prob_id = resolved_prob.problem_id if resolved_prob else problem_id
        prob_title = resolved_prob.title if resolved_prob else problem_id

        target_contest_id = contest_id
        if not target_contest_id:
            for c in self.list_contests():
                if c.status == ContestStatus.LIVE and canonical_prob_id in c.problem_ids:
                    target_contest_id = c.contest_id
                    break

        sub = Submission(
            submission_id=submission_id,
            problem_id=canonical_prob_id,
            problem_title=prob_title,
            user_id=user_id,
            user_name=user_name,
            source_file=source_file,
            source_code=source_code,
            contest_id=target_contest_id,
            time_taken_seconds=time_taken_seconds,
            execution_result=execution_result or ExecutionResult(),
            submitted_at=now,
        )

        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO submissions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sub.submission_id,
                    sub.problem_id,
                    sub.problem_title,
                    sub.user_id,
                    sub.user_name,
                    sub.source_file,
                    sub.source_code,
                    sub.contest_id,
                    sub.time_taken_seconds,
                    json_dump_helper(sub.execution_result.model_dump()),
                    sub.submitted_at.isoformat(),
                ),
            )

            if target_contest_id:
                contest = self.get_contest(target_contest_id)
                if contest:
                    if user_id not in contest.participants:
                        contest.participants[user_id] = ContestParticipant(user_id=user_id, user_name=user_name)
                    part = contest.participants[user_id]
                    if execution_result and execution_result.status == "Accepted":
                        if canonical_prob_id not in part.solved_problem_ids:
                            part.solved_problem_ids.append(canonical_prob_id)
                            part.score += 100
                            part.solved_timestamps[canonical_prob_id] = now.isoformat()
                            elapsed_min = max(0.0, (now - contest.start_time).total_seconds() / 60.0)
                            part.penalty_time_sec += elapsed_min * 60.0

                    parts_data = {uid: p.model_dump() for uid, p in contest.participants.items()}
                    conn.execute(
                        "UPDATE contests SET participants = ? WHERE contest_id = ?",
                        (json_dump_helper(parts_data), contest.contest_id),
                    )
            conn.commit()

        return sub

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM submissions WHERE submission_id = ?", (submission_id,)).fetchone()
            if not row:
                return None
            return self._row_to_submission(row)

    def get_problem_submissions(self, problem_id_or_slug: str) -> List[Submission]:
        prob = self.get_problem(problem_id_or_slug)
        pid = prob.problem_id if prob else problem_id_or_slug
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM submissions WHERE problem_id = ? OR problem_id = ? ORDER BY submitted_at DESC",
                (pid, problem_id_or_slug),
            ).fetchall()
            return [self._row_to_submission(r) for r in rows]

    def get_user_submissions(self, user_id: str) -> List[Submission]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM submissions WHERE user_id = ? ORDER BY submitted_at DESC",
                (user_id,),
            ).fetchall()
            return [self._row_to_submission(r) for r in rows]

    def _row_to_submission(self, row) -> Submission:
        return Submission(
            submission_id=row["submission_id"],
            problem_id=row["problem_id"],
            problem_title=row["problem_title"] or row["problem_id"],
            user_id=row["user_id"],
            user_name=row["user_name"],
            source_file=row["source_file"],
            source_code=row["source_code"],
            contest_id=row["contest_id"],
            time_taken_seconds=row["time_taken_seconds"] or 0.0,
            execution_result=ExecutionResult(**json.loads(row["execution_result"])),
            submitted_at=datetime.fromisoformat(row["submitted_at"]),
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
        now_str = datetime.now(timezone.utc).isoformat()
        prob_ids = problem_ids or [p.problem_id for p in self.list_problems()]

        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO contests VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    contest_id,
                    title,
                    description,
                    start.isoformat(),
                    duration_minutes,
                    json_dump_helper(prob_ids),
                    json_dump_helper({}),
                    now_str,
                ),
            )
            conn.commit()

        return self.get_contest(contest_id)

    def get_contest(self, contest_id: str) -> Optional[Contest]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM contests WHERE contest_id = ?", (contest_id,)).fetchone()
            if not row:
                return None
            
            parts_raw = json.loads(row["participants"] or "{}")
            participants = {
                uid: ContestParticipant(
                    user_id=p["user_id"],
                    user_name=p["user_name"],
                    registered_at=datetime.fromisoformat(p["registered_at"]) if isinstance(p["registered_at"], str) else p["registered_at"],
                    score=p["score"],
                    penalty_time_sec=p["penalty_time_sec"],
                    solved_problem_ids=p.get("solved_problem_ids", []),
                    solved_timestamps=p.get("solved_timestamps", {}),
                )
                for uid, p in parts_raw.items()
            }

            return Contest(
                contest_id=row["contest_id"],
                title=row["title"],
                description=row["description"],
                start_time=datetime.fromisoformat(row["start_time"]),
                duration_minutes=row["duration_minutes"],
                problem_ids=json.loads(row["problem_ids"] or "[]"),
                participants=participants,
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_contests(self) -> List[Contest]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT contest_id FROM contests ORDER BY start_time DESC").fetchall()
            return [self.get_contest(r["contest_id"]) for r in rows if r]

    def register_contest_participant(self, contest_id: str, user_id: str, user_name: str) -> Optional[ContestParticipant]:
        contest = self.get_contest(contest_id)
        if not contest:
            return None

        if user_id not in contest.participants:
            contest.participants[user_id] = ContestParticipant(user_id=user_id, user_name=user_name)
            parts_data = {uid: p.model_dump() for uid, p in contest.participants.items()}
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE contests SET participants = ? WHERE contest_id = ?",
                    (json_dump_helper(parts_data), contest_id),
                )
                conn.commit()

        return contest.participants[user_id]

    def get_contest_leaderboard(self, contest_id: str) -> Optional[ContestLeaderboardResponse]:
        contest = self.get_contest(contest_id)
        if not contest:
            return None

        problems_list = []
        for pid in contest.problem_ids:
            p = self.get_problem(pid)
            if p:
                problems_list.append(
                    ProblemSummaryResponse(
                        problem_id=p.problem_id,
                        title=p.title,
                        slug=p.slug,
                        difficulty=p.difficulty,
                        category=p.category,
                        topic_tags=p.topic_tags,
                    )
                )

        standings_data: List[LeaderboardRow] = []

        with self._get_conn() as conn:
            all_subs = [
                self._row_to_submission(r)
                for r in conn.execute(
                    "SELECT * FROM submissions WHERE contest_id = ? ORDER BY submitted_at ASC",
                    (contest_id,),
                ).fetchall()
            ]

        for uid, part in contest.participants.items():
            user_subs = [s for s in all_subs if s.user_id == uid]
            problem_results: Dict[str, LeaderboardProblemCell] = {}
            total_penalty_min = 0.0
            solved_count = 0

            for pid in contest.problem_ids:
                prob_obj = self.get_problem(pid)
                prob_subs = [
                    s for s in user_subs
                    if s.problem_id == pid or (prob_obj and s.problem_id == prob_obj.slug)
                ]

                if not prob_subs:
                    problem_results[pid] = LeaderboardProblemCell(
                        problem_id=pid,
                        status="UNTOUCHED",
                        attempts_count=0,
                    )
                    continue

                attempts_before_ac = 0
                is_ac = False
                ac_time_min = None

                for s in prob_subs:
                    attempts_before_ac += 1
                    if s.execution_result.status == "Accepted":
                        is_ac = True
                        c_start = contest.start_time if contest.start_time.tzinfo else contest.start_time.replace(tzinfo=timezone.utc)
                        s_time = s.submitted_at if s.submitted_at.tzinfo else s.submitted_at.replace(tzinfo=timezone.utc)
                        ac_time_min = round(max(0.0, (s_time - c_start).total_seconds() / 60.0), 1)
                        break

                if is_ac:
                    solved_count += 1
                    penalty_for_prob = (ac_time_min or 0.0) + (max(0, attempts_before_ac - 1) * 10.0)
                    total_penalty_min += penalty_for_prob
                    problem_results[pid] = LeaderboardProblemCell(
                        problem_id=pid,
                        status="SOLVED",
                        attempts_count=attempts_before_ac,
                        solved_time_min=ac_time_min,
                    )
                else:
                    problem_results[pid] = LeaderboardProblemCell(
                        problem_id=pid,
                        status="ATTEMPTED",
                        attempts_count=attempts_before_ac,
                    )

            standings_data.append(
                LeaderboardRow(
                    rank=1,
                    user_id=uid,
                    user_name=part.user_name,
                    score=solved_count * 100,
                    problems_solved=solved_count,
                    total_penalty_min=round(total_penalty_min, 1),
                    problem_results=problem_results,
                )
            )

        standings_data.sort(key=lambda r: (-r.score, r.total_penalty_min))
        for idx, row in enumerate(standings_data):
            row.rank = idx + 1

        return ContestLeaderboardResponse(
            contest_id=contest.contest_id,
            title=contest.title,
            status=contest.status.value,
            is_locked=contest.status == ContestStatus.FINISHED,
            problems=problems_list,
            standings=standings_data,
        )

    # --- Profile & Activity Heatmap ---

    def get_user_profile_stats(self, user_id: str, user_name: str, handle: str) -> UserProfileStats:
        all_problems = self.list_problems()
        user_subs = self.get_user_submissions(user_id)

        solved_prob_ids = set(s.problem_id for s in user_subs if s.execution_result.status == "Accepted")

        easy_total = sum(1 for p in all_problems if p.difficulty.lower() == "easy")
        medium_total = sum(1 for p in all_problems if p.difficulty.lower() == "medium")
        hard_total = sum(1 for p in all_problems if p.difficulty.lower() == "hard")

        easy_solved = sum(1 for p in all_problems if p.difficulty.lower() == "easy" and p.problem_id in solved_prob_ids)
        medium_solved = sum(1 for p in all_problems if p.difficulty.lower() == "medium" and p.problem_id in solved_prob_ids)
        hard_solved = sum(1 for p in all_problems if p.difficulty.lower() == "hard" and p.problem_id in solved_prob_ids)

        total_solved = len(solved_prob_ids)
        total_sub_count = len(user_subs)
        ac_count = sum(1 for s in user_subs if s.execution_result.status == "Accepted")
        acc_rate = round((ac_count / total_sub_count * 100.0), 1) if total_sub_count > 0 else 0.0

        heatmap_activity: Dict[str, int] = {}
        for s in user_subs:
            day_str = s.submitted_at.strftime("%Y-%m-%d")
            heatmap_activity[day_str] = heatmap_activity.get(day_str, 0) + 1

        recent_submissions = [
            SubmissionRecordResponse(
                submission_id=s.submission_id,
                problem_id=s.problem_id,
                problem_title=s.problem_title,
                user_id=s.user_id,
                user_name=s.user_name,
                status=s.execution_result.status,
                passed_test_cases=s.execution_result.passed_test_cases,
                total_test_cases=s.execution_result.total_test_cases,
                execution_time_ms=s.execution_result.execution_time_ms,
                memory_mb=s.execution_result.memory_mb,
                time_taken_seconds=s.time_taken_seconds,
                source_code=s.source_code,
                error_message=s.execution_result.error_message,
                stdout=s.execution_result.stdout,
                stderr=s.execution_result.stderr,
                submitted_at=s.submitted_at.isoformat(),
            )
            for s in user_subs[:15]
        ]

        return UserProfileStats(
            user_id=user_id,
            user_name=user_name,
            handle=handle,
            rank=1556455,
            total_solved=total_solved,
            total_problems=len(all_problems),
            easy_solved=easy_solved,
            easy_total=max(1, easy_total),
            medium_solved=medium_solved,
            medium_total=max(1, medium_total),
            hard_solved=hard_solved,
            hard_total=max(1, hard_total),
            acceptance_rate=acc_rate,
            total_submissions=total_sub_count,
            recent_submissions=recent_submissions,
            heatmap_activity=heatmap_activity,
        )