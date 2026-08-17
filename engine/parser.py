# engine/parser.py

from dataclasses import dataclass
from typing import List
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Node, Parser


@dataclass
class Token:
    """Represents a single normalized token along with its source location."""
    value: str       # e.g., 'VAR', 'FUNC', 'TYPE', 'for', 'if', '+'
    start_byte: int  # Starting byte offset in original source
    end_byte: int    # Ending byte offset in original source
    start_line: int  # Line number in original source (1-indexed)
    end_line: int    # Line number in original source (1-indexed)


class CppNormalizer:
    def __init__(self):
        # 1. Initialize Tree-sitter with C++ grammar
        self.language = Language(tscpp.language())
        self.parser = Parser(self.language)

    def normalize(self, source_code: str) -> List[Token]:
        """
        Parses C++ source code into an AST, strips comments/whitespace,
        and converts identifiers into canonical tokens (VAR, FUNC, TYPE).
        """
        source_bytes = bytes(source_code, "utf8")
        tree = self.parser.parse(source_bytes)
        
        tokens: List[Token] = []
        self._traverse(tree.root_node, source_bytes, tokens)
        return tokens

    def _traverse(self, node: Node, source_bytes: bytes, tokens: List[Token]):
        # 1. Strip comments completely
        if node.type == "comment":
            return

        # 2. If it's a leaf node (a terminal token with no children)
        if len(node.children) == 0:
            token_val = self._classify_leaf_node(node, source_bytes)
            if token_val:  # Ignore empty or whitespace-only nodes
                tokens.append(
                    Token(
                        value=token_val,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        start_line=node.start_point[0] + 1,  # Convert 0-indexed to 1-indexed
                        end_line=node.end_point[0] + 1,
                    )
                )
            return

        # 3. Otherwise, recursively visit all child nodes in order
        for child in node.children:
            self._traverse(child, source_bytes, tokens)

    def _classify_leaf_node(self, node: Node, source_bytes: bytes) -> str:
        """Classifies a terminal leaf node into a normalized representation."""
        node_text = source_bytes[node.start_byte:node.end_byte].decode("utf8").strip()
        if not node_text:
            return ""

        parent = node.parent
        parent_type = parent.type if parent else ""

        # A. Types (int, double, long long, custom classes, etc.)
        if node.type in ("primitive_type", "type_identifier"):
            return "TYPE"

        # B. Function Names (declaration, definition, or function calls)
        if node.type == "identifier":
            if parent_type in ("function_declarator", "call_expression"):
                return "FUNC"
            # C. Variable / parameter / generic identifiers
            return "VAR"

        # D. Literals (e.g., numbers, strings)
        if "literal" in node.type:
            return "LITERAL"

        # E. Language keywords and operators (for, while, if, +, -, {, }, ;, etc.)
        return node_text