# engine/single_auditor.py

import re
from typing import List, Optional, Set
from engine.models import IntegrityReport, Problem, Submission


def _normalize_cpp_tokens(code: str) -> List[str]:
    """Strips comments/strings and normalizes identifiers and literals to generic tokens."""
    clean = re.sub(r"//.*", "", code)
    clean = re.sub(r"/\*[\s\S]*?\*/", "", clean)
    clean = re.sub(r'"(\\.|[^"\\])*"', '""', clean)

    keywords = {
        "int", "long", "float", "double", "char", "bool", "void", "auto",
        "vector", "string", "unordered_map", "map", "unordered_set", "set",
        "if", "else", "for", "while", "do", "return", "break", "continue",
        "switch", "case", "class", "struct", "public", "private", "const",
    }

    raw_tokens = re.findall(r"[a-zA-Z_]\w*|[0-9]+|==|!=|<=|>=|\+\+|--|&&|\|\||[{}()\[\];,<>+\-*/%=]", clean)
    normalized = []

    for t in raw_tokens:
        if t in keywords:
            normalized.append(t)
        elif re.match(r"^[0-9]+$", t):
            normalized.append("NUM")
        elif re.match(r"^[a-zA-Z_]\w*$", t):
            normalized.append("ID")
        else:
            normalized.append(t)

    return normalized


def _extract_kgrams(tokens: List[str], k: int = 5) -> Set[str]:
    if len(tokens) < k:
        return {"_".join(tokens)} if tokens else set()
    return {"_".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def _calculate_similarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    kgrams_a = _extract_kgrams(tokens_a, k=5)
    kgrams_b = _extract_kgrams(tokens_b, k=5)
    if not kgrams_a or not kgrams_b:
        return 0.0
    intersection = len(kgrams_a.intersection(kgrams_b))
    union = len(kgrams_a.union(kgrams_b))
    return round((intersection / union) * 100.0, 1) if union > 0 else 0.0


def _detect_ai_patterns(code: str) -> tuple[float, str, List[str]]:
    flags = []
    score = 0.0

    # 1. AI Docstrings / Complexity Annotations
    if re.search(r"time\s+complexity\s*:", code, re.IGNORECASE):
        score += 30.0
        flags.append("AI Docstring: Explicit Time Complexity comment")
    if re.search(r"space\s+complexity\s*:", code, re.IGNORECASE):
        score += 25.0
        flags.append("AI Docstring: Explicit Space Complexity comment")

    # 2. Explanatory step-by-step commentary
    step_comments = re.findall(r"//\s*(step\s*\d+|initialize|base\s*case|iterate\s*through)", code, re.IGNORECASE)
    if len(step_comments) >= 2:
        score += 25.0
        flags.append(f"AI Commentary Style: {len(step_comments)} algorithmic phase labels")

    # 3. Formatted markdown blocks in comments
    if "```" in code:
        score += 35.0
        flags.append("Markdown code fencing artifacts detected")

    # 4. Canonical variable names
    if re.search(r"\b(current_sum|left_ptr|right_ptr|seen_elements)\b", code):
        score += 15.0
        flags.append("Canonical AI variable naming pattern")

    ai_prob = min(98.5, score)
    if ai_prob >= 70.0:
        level = "High"
    elif ai_prob >= 40.0:
        level = "Medium"
    elif ai_prob >= 20.0:
        level = "Low"
    else:
        level = "Clean"

    return ai_prob, level, flags


def audit_single_submission(
    source_code: str,
    problem: Optional[Problem],
    existing_submissions: List[Submission],
    current_user_id: str,
) -> IntegrityReport:
    tokens_sub = _normalize_cpp_tokens(source_code)
    highest_sim = 0.0
    matched_sub_id = None
    matched_user = None

    for sub in existing_submissions:
        # Compare only with accepted submissions from other participants
        if sub.user_id == current_user_id:
            continue
        if not sub.execution_result or sub.execution_result.status != "Accepted":
            continue

        tokens_other = _normalize_cpp_tokens(sub.source_code)
        sim = _calculate_similarity(tokens_sub, tokens_other)
        if sim > highest_sim:
            highest_sim = sim
            matched_sub_id = sub.submission_id
            matched_user = sub.user_name

    ai_prob, ai_level, ai_flags = _detect_ai_patterns(source_code)
    forensic_flags = list(ai_flags)

    if highest_sim >= 85.0:
        verdict = "Plagiarized"
        forensic_flags.append(f"Critical AST similarity ({highest_sim}%) with {matched_user or 'existing solution'}")
    elif highest_sim >= 65.0:
        verdict = "Suspicious Similarity"
        forensic_flags.append(f"Moderate token overlap ({highest_sim}%) with {matched_user or 'existing solution'}")
    elif ai_level in ("High", "Medium"):
        verdict = "High AI Probability"
    else:
        verdict = "Clean"
        if not forensic_flags:
            forensic_flags.append("Clean AST Fingerprint • Human Origin Signature")

    return IntegrityReport(
        similarity_score=highest_sim,
        matched_submission_id=matched_sub_id,
        matched_user_name=matched_user,
        ai_probability=ai_prob,
        ai_risk_level=ai_level,
        verdict=verdict,
        forensic_flags=forensic_flags,
    )