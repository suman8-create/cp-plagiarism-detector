# engine/contest_auditor.py

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional
from engine.models import Contest, ContestAuditReport, ContestSimilarityMatrix, Problem, Submission, SuspectPair
from engine.single_auditor import _calculate_similarity, _detect_ai_patterns, _normalize_cpp_tokens


def _strip_boilerplate(code: str, starter_code: str) -> str:
    """Strips lines that are identical to the problem starter template to prevent false boilerplate matches."""
    if not starter_code:
        return code
    starter_lines = set(line.strip() for line in starter_code.splitlines() if len(line.strip()) > 3)
    user_lines = code.splitlines()
    filtered = [line for line in user_lines if line.strip() not in starter_lines]
    return "\n".join(filtered) if len(filtered) > 3 else code


def calculate_temporal_multiplier(delta_seconds: float) -> float:
    """Calculates temporal proximity multiplier: 0-3 mins -> 1.35x, 3-10 mins -> 1.15x, >30 mins -> 1.0x"""
    mins = delta_seconds / 60.0
    if mins <= 3.0:
        return 1.35
    elif mins <= 10.0:
        return 1.18
    elif mins <= 25.0:
        return 1.08
    return 1.0


def audit_contest_batch(
    contest: Contest,
    contest_problems: List[Problem],
    contest_submissions: List[Submission],
) -> ContestAuditReport:
    audited_time_str = datetime.now(timezone.utc).isoformat()
    prob_map = {p.problem_id: p for p in contest_problems}

    matrices: List[ContestSimilarityMatrix] = []
    suspect_pairs: List[SuspectPair] = []
    total_subs_count = len(contest_submissions)

    # Group accepted submissions by problem_id -> user_id -> latest Submission
    for prob in contest_problems:
        pid = prob.problem_id
        prob_subs = [s for s in contest_submissions if s.problem_id == pid and s.execution_result and s.execution_result.status == "Accepted"]

        # Keep best/latest submission per user for this problem
        user_best_sub: Dict[str, Submission] = {}
        for s in prob_subs:
            user_best_sub[s.user_id] = s

        participants = list(user_best_sub.keys())
        p_count = len(participants)

        # Initialize N x N similarity matrix
        sim_matrix = [[100.0 if i == j else 0.0 for j in range(p_count)] for i in range(p_count)]
        p_names = [user_best_sub[uid].user_name for uid in participants]

        # Normalized token cache
        clean_tokens_cache = {}
        for uid in participants:
            raw_code = user_best_sub[uid].source_code
            stripped_code = _strip_boilerplate(raw_code, prob.starter_code)
            clean_tokens_cache[uid] = _normalize_cpp_tokens(stripped_code)

        # Pairwise comparison
        for i in range(p_count):
            for j in range(i + 1, p_count):
                u_a = participants[i]
                u_b = participants[j]
                sub_a = user_best_sub[u_a]
                sub_b = user_best_sub[u_b]

                ast_sim = _calculate_similarity(clean_tokens_cache[u_a], clean_tokens_cache[u_b])
                sim_matrix[i][j] = ast_sim
                sim_matrix[j][i] = ast_sim

                # Calculate temporal distance
                dt_a = sub_a.submitted_at if sub_a.submitted_at.tzinfo else sub_a.submitted_at.replace(tzinfo=timezone.utc)
                dt_b = sub_b.submitted_at if sub_b.submitted_at.tzinfo else sub_b.submitted_at.replace(tzinfo=timezone.utc)
                delta_sec = abs((dt_a - dt_b).total_seconds())

                time_multiplier = calculate_temporal_multiplier(delta_sec)
                composite_suspicion = round(min(100.0, ast_sim * time_multiplier), 1)

                # Flag suspicious pairs (Similarity >= 65% or high composite suspicion)
                if composite_suspicion >= 65.0 or ast_sim >= 70.0:
                    flags = []
                    if ast_sim >= 85.0:
                        flags.append(f"Critical AST Structure Overlap ({ast_sim}%)")
                    elif ast_sim >= 65.0:
                        flags.append(f"Substantial Token Sequence Overlap ({ast_sim}%)")

                    if delta_sec <= 180.0:
                        flags.append(f"High Temporal Correlation: Submissions submitted within {round(delta_sec)}s of each other")
                    elif delta_sec <= 600.0:
                        flags.append(f"Moderate Temporal Window: Submissions submitted within {round(delta_sec/60, 1)}m")

                    # AI check on both submissions
                    _, ai_level_a, ai_flags_a = _detect_ai_patterns(sub_a.source_code)
                    _, ai_level_b, _ = _detect_ai_patterns(sub_b.source_code)
                    if ai_level_a in ("High", "Medium") or ai_level_b in ("High", "Medium"):
                        flags.append("AI Syntactic Generation Signature detected in candidate code")

                    suspect_pairs.append(
                        SuspectPair(
                            user_a_id=u_a,
                            user_a_name=sub_a.user_name,
                            user_b_id=u_b,
                            user_b_name=sub_b.user_name,
                            problem_id=pid,
                            problem_title=prob.title,
                            ast_similarity=ast_sim,
                            time_delta_seconds=round(delta_sec, 1),
                            suspicion_score=composite_suspicion,
                            status="FLAGGED",
                            user_a_sub_id=sub_a.submission_id,
                            user_b_sub_id=sub_b.submission_id,
                            user_a_code=sub_a.source_code,
                            user_b_code=sub_b.source_code,
                            flags=flags,
                        )
                    )

        matrices.append(
            ContestSimilarityMatrix(
                problem_id=pid,
                problem_title=prob.title,
                participant_ids=participants,
                participant_names=p_names,
                matrix=sim_matrix,
            )
        )

    # Sort suspect pairs by highest suspicion score first
    suspect_pairs.sort(key=lambda sp: -sp.suspicion_score)

    return ContestAuditReport(
        contest_id=contest.contest_id,
        contest_title=contest.title,
        audited_at=audited_time_str,
        total_participants=len(contest.participants),
        total_submissions_audited=total_subs_count,
        flagged_pairs_count=len(suspect_pairs),
        similarity_matrices=matrices,
        suspect_pairs=suspect_pairs,
    )