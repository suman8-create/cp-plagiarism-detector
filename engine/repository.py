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
    return json.dumps(data, default=str)


class AssessmentRepository:
    def __init__(self):
        self._init_db()
        self._seed_default_users()
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

    def _seed_default_users(self):
        default_accounts = [
            ("std_suman_01", "suman", "Suman", "password123"),
            ("std_alex_101", "alex", "Alex Developer", "password123"),
            ("std_priya_202", "priya", "Priya Sharma", "password123"),
        ]
        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            for uid, uname, dname, pw in default_accounts:
                existing = conn.execute("SELECT user_id FROM users WHERE username = ?", (uname,)).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                        (uid, uname, dname, self._hash_pw(pw), now),
                    )
            conn.commit()

    def register_user(self, username: str, display_name: str, password: str) -> Dict:
        username_clean = username.strip().lower().replace("@", "")
        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters long.")
        with self._get_conn() as conn:
            existing = conn.execute("SELECT * FROM users WHERE username = ?", (username_clean,)).fetchone()
            if existing:
                raise ValueError(f"Username '@{username_clean}' is already taken.")

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

    def _seed_default_problems(self):
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()["c"]
            if count >= 15:
                return

        problems_seed = [
            {
                "title": "Two Sum",
                "category": "Algorithms",
                "topic_tags": ["Array", "Hash Table"],
                "difficulty": "Easy",
                "desc": "Given an array of integers nums and target, return indices of two numbers adding to target.",
                "starter": """#include <iostream>\n#include <vector>\n#include <unordered_map>\nusing namespace std;\nvector<int> twoSum(const vector<int>& nums, int target) {\n    unordered_map<int, int> seen;\n    for(int i=0; i<nums.size(); ++i) {\n        int comp = target - nums[i];\n        if(seen.count(comp)) return {seen[comp], i};\n        seen[nums[i]] = i;\n    }\n    return {};\n}\nint main(){\n    int n, target;\n    if(cin >> n >> target){\n        vector<int> nums(n);\n        for(int i=0; i<n; ++i) cin >> nums[i];\n        auto res = twoSum(nums, target);\n        if(!res.empty()) cout << res[0] << " " << res[1] << endl;\n    }\n    return 0;\n}""",
                "constraints": ["2 <= nums.length <= 10^4"],
                "examples": [{"input": "4 9\\n2 7 11 15", "output": "0 1"}],
                "tc": [TestCase(input_data="4 9\n2 7 11 15", expected_output="0 1", is_sample=True)]
            },
            {
                "title": "Fibonacci Number",
                "category": "Algorithms",
                "topic_tags": ["Math", "Dynamic Programming"],
                "difficulty": "Easy",
                "desc": "Calculate F(n) for given n.",
                "starter": """#include <iostream>\nusing namespace std;\nint fib(int n) {\n    if(n<=1) return n;\n    int a=0, b=1;\n    for(int i=2; i<=n; ++i){ int c=a+b; a=b; b=c; }\n    return b;\n}\nint main(){\n    int n;\n    if(cin >> n) cout << fib(n) << endl;\n    return 0;\n}""",
                "constraints": ["0 <= n <= 30"],
                "examples": [{"input": "4", "output": "3"}],
                "tc": [TestCase(input_data="4", expected_output="3", is_sample=True)]
            },
            {
                "title": "Add Two Numbers",
                "category": "Algorithms",
                "topic_tags": ["Math", "Simulation"],
                "difficulty": "Medium",
                "desc": "Given two integers a and b, compute their sum.",
                "starter": """#include <iostream>\nusing namespace std;\nint main(){\n    long long a, b;\n    if(cin >> a >> b) cout << (a+b) << endl;\n    return 0;\n}""",
                "constraints": ["-10^18 <= a, b <= 10^18"],
                "examples": [{"input": "12 28", "output": "40"}],
                "tc": [TestCase(input_data="12 28", expected_output="40", is_sample=True)]
            },
            {
                "title": "Valid Palindrome",
                "category": "Algorithms",
                "topic_tags": ["String", "Two Pointers"],
                "difficulty": "Easy",
                "desc": "Check if a given string is a palindrome ignoring case and alphanumeric characters.",
                "starter": """#include <iostream>\n#include <string>\n#include <cctype>\nusing namespace std;\nbool isPalindrome(string s) {\n    int l = 0, r = (int)s.size() - 1;\n    while(l < r) {\n        while(l < r && !isalnum(s[l])) l++;\n        while(l < r && !isalnum(s[r])) r--;\n        if(tolower(s[l]) != tolower(s[r])) return false;\n        l++; r--;\n    }\n    return true;\n}\nint main() {\n    string s;\n    if(getline(cin, s)) cout << (isPalindrome(s) ? "true" : "false") << endl;\n    return 0;\n}""",
                "constraints": ["1 <= s.length <= 2 * 10^5"],
                "examples": [{"input": "race a car", "output": "false"}],
                "tc": [TestCase(input_data="race a car", expected_output="false", is_sample=True)]
            },
            {
                "title": "Maximum Subarray",
                "category": "Algorithms",
                "topic_tags": ["Array", "Dynamic Programming"],
                "difficulty": "Medium",
                "desc": "Find the subarray with the largest sum and return its sum.",
                "starter": """#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\nint maxSubArray(const vector<int>& nums) {\n    int cur = nums[0], max_s = nums[0];\n    for(size_t i=1; i<nums.size(); ++i) {\n        cur = max(nums[i], cur + nums[i]);\n        max_s = max(max_s, cur);\n    }\n    return max_s;\n}\nint main() {\n    int n;\n    if(cin >> n) {\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        cout << maxSubArray(a) << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= nums.length <= 10^5"],
                "examples": [{"input": "5\\n-2 1 -3 4 -1", "output": "4"}],
                "tc": [TestCase(input_data="5\n-2 1 -3 4 -1", expected_output="4", is_sample=True)]
            },
            {
                "title": "Climbing Stairs",
                "category": "Algorithms",
                "topic_tags": ["Math", "Dynamic Programming"],
                "difficulty": "Easy",
                "desc": "You are climbing a staircase. It takes n steps to reach the top. How many distinct ways can you climb to the top taking 1 or 2 steps?",
                "starter": """#include <iostream>\nusing namespace std;\nint climbStairs(int n) {\n    if(n<=2) return n;\n    int a=1, b=2;\n    for(int i=3; i<=n; ++i){\n        int c = a + b;\n        a = b;\n        b = c;\n    }\n    return b;\n}\nint main() {\n    int n;\n    if(cin >> n) cout << climbStairs(n) << endl;\n    return 0;\n}""",
                "constraints": ["1 <= n <= 45"],
                "examples": [{"input": "3", "output": "3"}],
                "tc": [TestCase(input_data="3", expected_output="3", is_sample=True)]
            },
            {
                "title": "Contains Duplicate",
                "category": "Algorithms",
                "topic_tags": ["Array", "Hash Table"],
                "difficulty": "Easy",
                "desc": "Given an integer array nums, return true if any value appears at least twice in the array.",
                "starter": """#include <iostream>\n#include <vector>\n#include <unordered_set>\nusing namespace std;\nbool containsDuplicate(const vector<int>& nums) {\n    unordered_set<int> s;\n    for(int x : nums) { if(s.count(x)) return true; s.insert(x); }\n    return false;\n}\nint main() {\n    int n;\n    if(cin >> n) {\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        cout << (containsDuplicate(a) ? "true" : "false") << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= nums.length <= 10^5"],
                "examples": [{"input": "4\\n1 2 3 1", "output": "true"}],
                "tc": [TestCase(input_data="4\n1 2 3 1", expected_output="true", is_sample=True)]
            },
            {
                "title": "Reverse String",
                "category": "Algorithms",
                "topic_tags": ["String", "Two Pointers"],
                "difficulty": "Easy",
                "desc": "Write a function that reverses a string in-place.",
                "starter": """#include <iostream>\n#include <string>\n#include <algorithm>\nusing namespace std;\nint main() {\n    string s;\n    if(cin >> s) {\n        reverse(s.begin(), s.end());\n        cout << s << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= s.length <= 10^5"],
                "examples": [{"input": "hello", "output": "olleh"}],
                "tc": [TestCase(input_data="hello", expected_output="olleh", is_sample=True)]
            },
            {
                "title": "Merge Sorted Array",
                "category": "Algorithms",
                "topic_tags": ["Array", "Two Pointers", "Sorting"],
                "difficulty": "Easy",
                "desc": "Merge two sorted arrays nums1 and nums2 into nums1 as one sorted array.",
                "starter": """#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\nint main() {\n    int m, n;\n    if(cin >> m >> n) {\n        vector<int> a(m+n);\n        for(int i=0; i<m; ++i) cin >> a[i];\n        for(int i=0; i<n; ++i) cin >> a[m+i];\n        sort(a.begin(), a.end());\n        for(int i=0; i<m+n; ++i) cout << a[i] << (i+1==m+n?"\\n":" ");\n    }\n    return 0;\n}""",
                "constraints": ["0 <= m, n <= 200"],
                "examples": [{"input": "3 3\\n1 2 3\\n2 5 6", "output": "1 2 2 3 5 6"}],
                "tc": [TestCase(input_data="3 3\n1 2 3\n2 5 6", expected_output="1 2 2 3 5 6", is_sample=True)]
            },
            {
                "title": "Best Time to Buy and Sell Stock",
                "category": "Algorithms",
                "topic_tags": ["Array", "Dynamic Programming"],
                "difficulty": "Easy",
                "desc": "Find the maximum profit you can achieve from buying and selling stock once.",
                "starter": """#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\nint maxProfit(const vector<int>& p) {\n    if(p.empty()) return 0;\n    int min_p = p[0], max_pro = 0;\n    for(size_t i=1; i<p.size(); ++i){\n        min_p = min(min_p, p[i]);\n        max_pro = max(max_pro, p[i] - min_p);\n    }\n    return max_pro;\n}\nint main(){\n    int n;\n    if(cin >> n){\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        cout << maxProfit(a) << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= prices.length <= 10^5"],
                "examples": [{"input": "6\\n7 1 5 3 6 4", "output": "5"}],
                "tc": [TestCase(input_data="6\n7 1 5 3 6 4", expected_output="5", is_sample=True)]
            },
            {
                "title": "Search Insert Position",
                "category": "Algorithms",
                "topic_tags": ["Array", "Binary Search"],
                "difficulty": "Easy",
                "desc": "Given a sorted array of distinct integers and a target value, return index if found or index where it would be inserted.",
                "starter": """#include <iostream>\n#include <vector>\nusing namespace std;\nint searchInsert(const vector<int>& nums, int target) {\n    int l = 0, r = (int)nums.size() - 1;\n    while(l <= r) {\n        int mid = l + (r-l)/2;\n        if(nums[mid] == target) return mid;\n        else if(nums[mid] < target) l = mid + 1;\n        else r = mid - 1;\n    }\n    return l;\n}\nint main() {\n    int n, target;\n    if(cin >> n >> target){\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        cout << searchInsert(a, target) << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= nums.length <= 10^4"],
                "examples": [{"input": "4 5\\n1 3 5 6", "output": "2"}],
                "tc": [TestCase(input_data="4 5\n1 3 5 6", expected_output="2", is_sample=True)]
            },
            {
                "title": "Single Number",
                "category": "Algorithms",
                "topic_tags": ["Array", "Bit Manipulation"],
                "difficulty": "Easy",
                "desc": "Every element appears twice except for one. Find that single one.",
                "starter": """#include <iostream>\n#include <vector>\nusing namespace std;\nint singleNumber(const vector<int>& nums) {\n    int res = 0;\n    for(int x : nums) res ^= x;\n    return res;\n}\nint main(){\n    int n;\n    if(cin >> n){\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        cout << singleNumber(a) << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= nums.length <= 3 * 10^4"],
                "examples": [{"input": "3\\n2 2 1", "output": "1"}],
                "tc": [TestCase(input_data="3\n2 2 1", expected_output="1", is_sample=True)]
            },
            {
                "title": "Missing Number",
                "category": "Algorithms",
                "topic_tags": ["Array", "Math", "Bit Manipulation"],
                "difficulty": "Easy",
                "desc": "Given an array nums containing n distinct numbers in the range [0, n], return the only number in the range that is missing.",
                "starter": """#include <iostream>\n#include <vector>\nusing namespace std;\nint missingNumber(const vector<int>& nums) {\n    int n = nums.size();\n    long long total = 1LL * n * (n + 1) / 2;\n    for(int x : nums) total -= x;\n    return total;\n}\nint main(){\n    int n;\n    if(cin >> n){\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        cout << missingNumber(a) << endl;\n    }\n    return 0;\n}""",
                "constraints": ["n == nums.length", "1 <= n <= 10^4"],
                "examples": [{"input": "3\\n3 0 1", "output": "2"}],
                "tc": [TestCase(input_data="3\n3 0 1", expected_output="2", is_sample=True)]
            },
            {
                "title": "Longest Common Prefix",
                "category": "Algorithms",
                "topic_tags": ["String", "Trie"],
                "difficulty": "Easy",
                "desc": "Write a function to find the longest common prefix string amongst an array of strings.",
                "starter": """#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\nstring longestCommonPrefix(vector<string>& strs) {\n    if(strs.empty()) return "";\n    string prefix = strs[0];\n    for(size_t i=1; i<strs.size(); ++i){\n        while(strs[i].find(prefix) != 0){\n            prefix = prefix.substr(0, prefix.size() - 1);\n            if(prefix.empty()) return "";\n        }\n    }\n    return prefix;\n}\nint main(){\n    int n;\n    if(cin >> n){\n        vector<string> s(n);\n        for(int i=0; i<n; ++i) cin >> s[i];\n        cout << longestCommonPrefix(s) << endl;\n    }\n    return 0;\n}""",
                "constraints": ["1 <= strs.length <= 200"],
                "examples": [{"input": "3\\nflower flow flight", "output": "fl"}],
                "tc": [TestCase(input_data="3\nflower flow flight", expected_output="fl", is_sample=True)]
            },
            {
                "title": "Move Zeroes",
                "category": "Algorithms",
                "topic_tags": ["Array", "Two Pointers"],
                "difficulty": "Easy",
                "desc": "Given an integer array nums, move all 0's to the end of it while maintaining relative order of non-zero elements.",
                "starter": """#include <iostream>\n#include <vector>\nusing namespace std;\nvoid moveZeroes(vector<int>& nums) {\n    int last = 0;\n    for(size_t i=0; i<nums.size(); ++i){\n        if(nums[i] != 0) nums[last++] = nums[i];\n    }\n    for(size_t i=last; i<nums.size(); ++i) nums[i] = 0;\n}\nint main(){\n    int n;\n    if(cin >> n){\n        vector<int> a(n);\n        for(int i=0; i<n; ++i) cin >> a[i];\n        moveZeroes(a);\n        for(int i=0; i<n; ++i) cout << a[i] << (i+1==n?"\\n":" ");\n    }\n    return 0;\n}""",
                "constraints": ["1 <= nums.length <= 10^4"],
                "examples": [{"input": "5\\n0 1 0 3 12", "output": "1 3 12 0 0"}],
                "tc": [TestCase(input_data="5\n0 1 0 3 12", expected_output="1 3 12 0 0", is_sample=True)]
            }
        ]

        for p in problems_seed:
            self.create_problem(
                title=p["title"],
                description=p["desc"],
                difficulty=p["difficulty"],
                category=p["category"],
                topic_tags=p["topic_tags"],
                starter_code=p["starter"],
                constraints=p["constraints"],
                examples=p["examples"],
                test_cases=p["tc"],
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
            problem_ids=[p_two_sum, p_fib],
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
        exec_res_raw = row["execution_result"] if "execution_result" in row.keys() else "{}"
        try:
            exec_dict = json.loads(exec_res_raw)
        except Exception:
            exec_dict = {}

        return Submission(
            submission_id=row["submission_id"],
            problem_id=row["problem_id"],
            problem_title=row["problem_title"] if "problem_title" in row.keys() and row["problem_title"] else row["problem_id"],
            user_id=row["user_id"],
            user_name=row["user_name"],
            source_file=row["source_file"] if "source_file" in row.keys() else "solution.cpp",
            source_code=row["source_code"] if "source_code" in row.keys() else "",
            contest_id=row["contest_id"] if "contest_id" in row.keys() else None,
            time_taken_seconds=row["time_taken_seconds"] if "time_taken_seconds" in row.keys() and row["time_taken_seconds"] else 0.0,
            execution_result=ExecutionResult(**exec_dict) if exec_dict else ExecutionResult(),
            submitted_at=datetime.fromisoformat(row["submitted_at"]) if "submitted_at" in row.keys() and row["submitted_at"] else datetime.now(timezone.utc),
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
        prob_ids = problem_ids or [p.problem_id for p in self.list_problems()[:2]]

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

    def get_user_profile_stats(self, user_id: str, fallback_name: Optional[str] = None, fallback_handle: Optional[str] = None) -> UserProfileStats:
        user_name = fallback_name or "Competitor"
        handle = fallback_handle or f"@{user_id}"

        with self._get_conn() as conn:
            try:
                user_row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
                if user_row:
                    user_name = user_row["display_name"]
                    raw_uname = user_row["username"]
                    handle = f"@{raw_uname}" if not raw_uname.startswith("@") else raw_uname
            except Exception:
                pass

        all_problems = self.list_problems()
        user_subs = self.get_user_submissions(user_id)

        solved_prob_ids = set(s.problem_id for s in user_subs if s.execution_result and s.execution_result.status == "Accepted")

        easy_total = sum(1 for p in all_problems if p.difficulty.lower() == "easy")
        medium_total = sum(1 for p in all_problems if p.difficulty.lower() == "medium")
        hard_total = sum(1 for p in all_problems if p.difficulty.lower() == "hard")

        easy_solved = sum(1 for p in all_problems if p.difficulty.lower() == "easy" and (p.problem_id in solved_prob_ids or p.slug in solved_prob_ids))
        medium_solved = sum(1 for p in all_problems if p.difficulty.lower() == "medium" and (p.problem_id in solved_prob_ids or p.slug in solved_prob_ids))
        hard_solved = sum(1 for p in all_problems if p.difficulty.lower() == "hard" and (p.problem_id in solved_prob_ids or p.slug in solved_prob_ids))

        total_solved = len(solved_prob_ids)
        total_sub_count = len(user_subs)
        ac_count = sum(1 for s in user_subs if s.execution_result and s.execution_result.status == "Accepted")
        acc_rate = round((ac_count / total_sub_count * 100.0), 1) if total_sub_count > 0 else 0.0

        heatmap_activity: Dict[str, int] = {}
        for s in user_subs:
            day_str = s.submitted_at.strftime("%Y-%m-%d")
            heatmap_activity[day_str] = heatmap_activity.get(day_str, 0) + 1

        recent_submissions = [
            SubmissionRecordResponse(
                submission_id=s.submission_id,
                problem_id=s.problem_id,
                problem_title=s.problem_title or s.problem_id,
                user_id=s.user_id,
                user_name=s.user_name,
                status=s.execution_result.status,
                passed_test_cases=s.execution_result.passed_test_cases,
                total_test_cases=s.execution_result.total_test_cases,
                execution_time_ms=s.execution_result.execution_time_ms,
                memory_mb=s.execution_result.memory_mb if hasattr(s.execution_result, "memory_mb") and s.execution_result.memory_mb else 46.38,
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
            total_problems=max(len(all_problems), 15),
            easy_solved=easy_solved,
            easy_total=max(easy_total, 10),
            medium_solved=medium_solved,
            medium_total=max(medium_total, 4),
            hard_solved=hard_solved,
            hard_total=max(hard_total, 1),
            acceptance_rate=acc_rate,
            total_submissions=total_sub_count,
            recent_submissions=recent_submissions,
            heatmap_activity=heatmap_activity,
        )