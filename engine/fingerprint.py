# engine/fingerprint.py

import hashlib
from dataclasses import dataclass
from typing import List, Set
from engine.parser import Token


@dataclass(frozen=True)
class Fingerprint:
    """Represents a discrete digital fingerprint with its location in source code."""
    hash_val: int
    start_line: int
    end_line: int

    def __eq__(self, other):
        return isinstance(other, Fingerprint) and self.hash_val == other.hash_val

    def __hash__(self):
        return hash(self.hash_val)


class WinnowingEngine:
    def __init__(self, k: int = 6, w: int = 4):
        """
        :param k: Size of each token n-gram (default: 6 tokens)
        :param w: Size of the sliding window for winnowing (default: 4 hashes)
        """
        self.k = k
        self.w = w

    def _hash_kgram(self, kgram_tokens: List[Token]) -> int:
        """Deterministically hashes a k-gram of tokens into a 64-bit unsigned integer."""
        token_str = " ".join(t.value for t in kgram_tokens)
        # Using MD5 truncated to 16 hex chars (64-bit integer) for cross-platform determinism
        hex_digest = hashlib.md5(token_str.encode("utf8")).hexdigest()[:16]
        return int(hex_digest, 16)

    def generate_fingerprints(self, tokens: List[Token]) -> List[Fingerprint]:
        """
        Converts a list of tokens into Winnowed fingerprints with line numbers.
        """
        if len(tokens) < self.k:
            return []

        # 1. Create all k-grams and their corresponding hashes + line spans
        kgrams = []
        for i in range(len(tokens) - self.k + 1):
            kgram = tokens[i : i + self.k]
            h = self._hash_kgram(kgram)
            start_line = kgram[0].start_line
            end_line = kgram[-1].end_line
            kgrams.append((h, start_line, end_line))

        # 2. If we have fewer k-grams than the window size w, take the minimum of what we have
        if len(kgrams) < self.w:
            min_kgram = min(kgrams, key=lambda item: item[0])
            return [Fingerprint(hash_val=min_kgram[0], start_line=min_kgram[1], end_line=min_kgram[2])]

        # 3. Slide a window of size w across k-gram hashes and pick the minimum
        fingerprints: List[Fingerprint] = []
        last_selected_idx = -1

        for window_start in range(len(kgrams) - self.w + 1):
            window = kgrams[window_start : window_start + self.w]
            
            # Find the minimum hash in the window.
            # In case of ties, select the rightmost occurrence (standard Winnowing rule)
            min_val = min(item[0] for item in window)
            min_idx_in_window = max(idx for idx, item in enumerate(window) if item[0] == min_val)
            global_min_idx = window_start + min_idx_in_window

            # Avoid recording duplicate consecutive fingerprints from the same position
            if global_min_idx != last_selected_idx:
                selected = kgrams[global_min_idx]
                fingerprints.append(
                    Fingerprint(
                        hash_val=selected[0],
                        start_line=selected[1],
                        end_line=selected[2],
                    )
                )
                last_selected_idx = global_min_idx

        return fingerprints