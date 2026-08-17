# engine/forensics.py

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ForensicReport:
    """Detailed report for AI code detection."""
    ai_confidence_score: float  # 0.0 to 100.0%
    is_suspicious: bool         # True if score >= 50.0%
    flags: List[str] = field(default_factory=list)


class LLMForensicEngine:
    # Invisible Unicode characters left by web rich-text copy-pasting
    INVISIBLE_UNICODE = {
        "\u200b": "Zero-Width Space (\\u200B)",
        "\u200c": "Zero-Width Non-Joiner (\\u200C)",
        "\u200d": "Zero-Width Joiner (\\u200D)",
        "\ufeff": "Zero-Width No-Break Space (\\uFEFF)",
        "\u00a0": "Non-Breaking Space (\\u00A0)",
    }

    # Regex patterns typical of ChatGPT / Claude explanations
    AI_COMMENT_PATTERNS = [
        (re.compile(r"//\s*(time|space)\s*complexity\s*:", re.IGNORECASE), "LLM Complexity Analysis Header", 35),
        (re.compile(r"//\s*(driver\s*code|main\s*function\s*to\s*test)", re.IGNORECASE), "LLM Boilerplate Marker ('Driver code')", 25),
        (re.compile(r"//\s*function\s+to\s+(solve|calculate|find|compute)", re.IGNORECASE), "Textbook AI Functional Comment", 20),
        (re.compile(r"//\s*base\s*case\b", re.IGNORECASE), "Textbook 'Base case' Annotation", 15),
        (re.compile(r"//\s*initialize\b", re.IGNORECASE), "Textbook 'Initialize' Annotation", 10),
    ]

    # Markdown remnants from direct copy-paste
    MARKDOWN_PATTERNS = [
        (re.compile(r"```(cpp|c\+\+|c)?", re.IGNORECASE), "Markdown Code Block Remnant (```)", 40),
        (re.compile(r"^\s*###?\s+", re.MULTILINE), "Markdown Header Remnant (#)", 30),
    ]

    def scan(self, raw_code: str) -> ForensicReport:
        """
        Scans raw C++ code for LLM copy-paste artifacts and returns an AI Confidence Score.
        """
        flags: List[str] = []
        raw_score = 0.0

        lines = raw_code.splitlines()

        # 1. Check for Invisible Unicode & Web Clipboard Artifacts
        for line_idx, line in enumerate(lines, start=1):
            for char, char_name in self.INVISIBLE_UNICODE.items():
                if char in line:
                    count = line.count(char)
                    flags.append(f"Line {line_idx}: Found {count}x {char_name} (Web copy-paste artifact)")
                    raw_score += 25 * count

        # 2. Check for Markdown Remnants
        for pattern, label, weight in self.MARKDOWN_PATTERNS:
            matches = pattern.findall(raw_code)
            if matches:
                flags.append(f"Detected {label}")
                raw_score += weight * len(matches)

        # 3. Check for AI Comment Signatures
        for line_idx, line in enumerate(lines, start=1):
            for pattern, label, weight in self.AI_COMMENT_PATTERNS:
                if pattern.search(line):
                    flags.append(f"Line {line_idx}: {label} -> '{line.strip()}'")
                    raw_score += weight

        # 4. Stylistic Heuristic: Over-Commented Ratio
        comment_lines = sum(1 for line in lines if line.strip().startswith("//") or line.strip().startswith("/*"))
        total_non_empty_lines = sum(1 for line in lines if line.strip())

        if total_non_empty_lines > 5:
            comment_ratio = comment_lines / total_non_empty_lines
            # In CP, > 25% comments is rare and heavily correlates with textbook AI answers
            if comment_ratio >= 0.25:
                flags.append(f"High Comment Density ({round(comment_ratio * 100, 1)}% of code is comments)")
                raw_score += 20

        # Cap score between 0.0% and 100.0%
        final_score = min(100.0, round(raw_score, 2))
        is_suspicious = final_score >= 50.0

        return ForensicReport(
            ai_confidence_score=final_score,
            is_suspicious=is_suspicious,
            flags=flags,
        )