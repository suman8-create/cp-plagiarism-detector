# 🛡️ CP Plagiarism Detector & LLM Forensic Engine

An end-to-end code plagiarism detection platform and AI forensics suite tailored for competitive programming contests, university labs, and coding assessments. 

The system couples **Abstract Syntax Tree (AST) normalization** and **Winnowing fingerprinting** with an **LLM Forensic Engine** that exposes ChatGPT/Claude-generated submissions, zero-width web clipboard watermarks, and structural clones.

---

## ✨ Key Features

### 1. 🌲 AST Token Normalization (Tree-sitter)
* Strips whitespace and comments while tokenizing source code via Tree-sitter C++ grammar.
* Replaces variable names, function identifiers, and custom type definitions with canonical placeholders (`VAR`, `FUNC`, `TYPE`, `LITERAL`).
* Defeats identifier renaming, variable swapping, and cosmetic formatting tampering.

### 2. ⚡ Winnowing & In-Memory Inverted Index
* Slices canonical token streams into $k$-grams ($k=6$) using rolling 64-bit Karp-Rabin hashing.
* Selects window minimums via sliding-window winnowing ($w=4$) to generate compact document fingerprints with coordinate mapping.
* Employs an in-memory inverted index (`hash -> {submission_ids}`) to prune candidate comparisons and bypass naive $O(N^2)$ evaluation.

### 3. 🧠 Dynamic Template Auto-Learner
* Dynamically calculates Document Frequency ($DF$) of fingerprints across contest batches.
* Automatically identifies and strips common contest starter code, headers, and fast I/O boilerplate ($\ge 50\%$ batch presence) to prevent false positives.

### 4. 🤖 AI Ghostwriter & Watermark Buster (LLM Forensics)
* **Invisible Unicode & Web Artifacts:** Scans raw character bytes for zero-width spaces (`\u200B`), non-breaking spaces (`\u00A0`), zero-width joiners (`\u200C`/`\u200D`), and byte order marks (`\uFEFF`) left behind by web browser copy-pasting.
* **AI Signature Detection:** Flags standard LLM docstrings and complexity headers (e.g., `// Time Complexity: O(...)`, `// Driver code`, `// Function to solve...`).
* **Markdown Remnants:** Detects leftover code-fence annotations (e.g., ```` ```cpp ````).
* **Comment Density Heuristics:** Flags abnormally high comment ratios that contrast with authentic timed contest solutions.

### 5. 🖥️ Interactive Visual Diff Dashboard
* Real-time drag-and-drop batch upload supporting multi-file `.cpp` selections and `.zip` contest archives.
* Pairwise similarity leaderboard ranked by Jaccard similarity percentage.
* Split-pane code viewer with synchronized line highlighting:
  * 🔴 **Red:** Detected structural plagiarism.
  * 🔵 **Blue:** Auto-ignored contest boilerplate.
  * 🤖 **Audit Trail:** Per-file breakdown of detected LLM signatures and confidence ratings.

---

## 🛠️ Tech Stack

* **Core Engine:** Python 3.10+, Tree-sitter (`tree-sitter-cpp`)
* **Backend API:** FastAPI, Uvicorn, Pydantic
* **Frontend:** React 18, Vite, Tailwind CSS v4, Lucide Icons

---

## 📁 Repository Structure

```text
cp-plagiarism-detector/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI endpoints (/api/check-plagiarism, /api/template-stats)
├── engine/
│   ├── __init__.py
│   ├── detector.py          # Similarity pipeline, inverted index, & template learner
│   ├── fingerprint.py       # K-gram hasher & Winnowing engine
│   ├── forensics.py         # LLM Ghostwriter & Unicode artifact scanner
│   └── parser.py            # Tree-sitter C++ AST token normalizer
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── DiffViewer.jsx # Side-by-side code diff modal
│   │   ├── App.jsx            # Main dashboard & AI audit UI
│   │   ├── index.css          # Tailwind styling
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── test_samples/            # Sample submissions for testing
├── test_api.py              # Automated API pipeline test
├── test_forensics.py        # Standalone LLM forensic scanner test
├── requirements.txt
└── README.md