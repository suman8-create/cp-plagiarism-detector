# engine/detector.py

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from engine.fingerprint import Fingerprint, WinnowingEngine
from engine.parser import CppNormalizer, Token


@dataclass
class MatchSpan:
    """Represents a highlighted code line interval."""
    start_line: int
    end_line: int


@dataclass
class ComparisonResult:
    """Comparison report between two submissions."""
    file_a: str
    file_b: str
    similarity_score: float  # 0.0 to 100.0%
    shared_fingerprints_count: int
    matched_lines_a: List[MatchSpan] = field(default_factory=list)
    matched_lines_b: List[MatchSpan] = field(default_factory=list)


@dataclass
class ProcessedSubmission:
    file_name: str
    code: str
    tokens: List[Token]
    fingerprints: List[Fingerprint]
    filtered_hashes: Set[int] = field(default_factory=set)
    boilerplate_lines: List[MatchSpan] = field(default_factory=list)


class PlagiarismDetector:
    def __init__(self, k: int = 6, w: int = 4, boilerplate_threshold: float = 0.50):
        self.normalizer = CppNormalizer()
        self.winnower = WinnowingEngine(k=k, w=w)
        self.boilerplate_threshold = boilerplate_threshold
        # Cache for latest template stats
        self.last_boilerplate_hashes: Set[int] = set()
        self.last_boilerplate_stats: Dict[str, any] = {}

    def analyze_submissions(self, files: Dict[str, str]) -> Tuple[List[ComparisonResult], Set[int], Dict[str, List[MatchSpan]]]:
        if len(files) < 2:
            return [], set(), {}

        # 1. Parse and fingerprint all submissions
        processed: Dict[str, ProcessedSubmission] = {}
        inverted_index_raw: Dict[int, Set[str]] = defaultdict(set)

        for filename, code in files.items():
            tokens = self.normalizer.normalize(code)
            fingerprints = self.winnower.generate_fingerprints(tokens)
            
            sub = ProcessedSubmission(
                file_name=filename,
                code=code,
                tokens=tokens,
                fingerprints=fingerprints,
            )
            processed[filename] = sub

            for fp in fingerprints:
                inverted_index_raw[fp.hash_val].add(filename)

        total_files = len(files)

        # 2. Dynamic Template Auto-Learner
        min_required_files = max(3, int(total_files * self.boilerplate_threshold))
        boilerplate_hashes: Set[int] = set()
        
        for hash_val, file_set in inverted_index_raw.items():
            if len(file_set) >= min_required_files:
                boilerplate_hashes.add(hash_val)

        self.last_boilerplate_hashes = boilerplate_hashes
        self.last_boilerplate_stats = {
            "total_files": total_files,
            "boilerplate_hashes_count": len(boilerplate_hashes),
            "threshold_used": self.boilerplate_threshold,
            "min_file_threshold": min_required_files,
        }

        # 3. Strip boilerplate & isolate boilerplate line spans for visualization
        inverted_index_filtered: Dict[int, Set[str]] = defaultdict(set)
        file_boilerplate_spans: Dict[str, List[MatchSpan]] = {}

        for filename, sub in processed.items():
            unique_hashes = {fp.hash_val for fp in sub.fingerprints}
            sub.filtered_hashes = unique_hashes - boilerplate_hashes
            
            # Map boilerplate line spans
            sub.boilerplate_lines = [
                MatchSpan(start_line=fp.start_line, end_line=fp.end_line)
                for fp in sub.fingerprints
                if fp.hash_val in boilerplate_hashes
            ]
            file_boilerplate_spans[filename] = sub.boilerplate_lines

            # Populate in-memory inverted index with clean hashes
            for h in sub.filtered_hashes:
                inverted_index_filtered[h].add(filename)

        # 4. Fast Inverted Index Candidate Pair Lookups (Avoids brute-force O(N^2))
        candidate_pairs: Set[Tuple[str, str]] = set()
        for hash_val, matched_files in inverted_index_filtered.items():
            matched_list = sorted(list(matched_files))
            for i in range(len(matched_list)):
                for j in range(i + 1, len(matched_list)):
                    candidate_pairs.add((matched_list[i], matched_list[j]))

        # 5. Jaccard Similarity Scoring on Candidate Pairs
        results: List[ComparisonResult] = []
        
        for file_a, file_b in candidate_pairs:
            sub_a = processed[file_a]
            sub_b = processed[file_b]

            shared_hashes = sub_a.filtered_hashes.intersection(sub_b.filtered_hashes)
            union_hashes = sub_a.filtered_hashes.union(sub_b.filtered_hashes)

            similarity = len(shared_hashes) / len(union_hashes) if union_hashes else 0.0

            matched_spans_a = [
                MatchSpan(start_line=fp.start_line, end_line=fp.end_line)
                for fp in sub_a.fingerprints
                if fp.hash_val in shared_hashes
            ]
            matched_spans_b = [
                MatchSpan(start_line=fp.start_line, end_line=fp.end_line)
                for fp in sub_b.fingerprints
                if fp.hash_val in shared_hashes
            ]

            results.append(
                ComparisonResult(
                    file_a=file_a,
                    file_b=file_b,
                    similarity_score=round(similarity * 100, 2),
                    shared_fingerprints_count=len(shared_hashes),
                    matched_lines_a=matched_spans_a,
                    matched_lines_b=matched_spans_b,
                )
            )

        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results, boilerplate_hashes, file_boilerplate_spans