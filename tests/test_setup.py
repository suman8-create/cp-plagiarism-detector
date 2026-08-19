# test_setup.py
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

# 1. Load the compiled C++ grammar
CPP_LANGUAGE = Language(tscpp.language())

# 2. Initialize the parser with the C++ grammar
parser = Parser(CPP_LANGUAGE)

# 3. Simple C++ test snippet
sample_code = """
int main() {
    return 0;
}
"""

# 4. Parse the source code (Tree-sitter expects bytes)
tree = parser.parse(bytes(sample_code, "utf8"))

# 5. Inspect the root node of the syntax tree
print("✅ Tree-sitter is ready!")
print("Root Node Type:", tree.root_node.type)
print("S-Expression:", tree.root_node)