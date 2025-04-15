import os
import re
import ast
import shutil
import zipfile
import tempfile
import tokenize

# ---- CONFIG ----
ZIP_FOLDER = "../"  # Path to the folder containing zipped repositories

# ---- HELPERS ----

def unzip_repo(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def extract_readme(repo_path):
    readme_text = ""
    for root, _, files in os.walk(repo_path):
        for fname in files:
            if fname.lower().startswith("readme"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        readme_text += f.read()
                except Exception:
                    pass
    return readme_text

def extract_docstrings_comments(filepath):
    docstrings = []
    comments = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings.append(doc)
    except Exception:
        pass
    try:
        with open(filepath, 'rb') as f:
            for toktype, tok, *_ in tokenize.tokenize(f.readline):
                if toktype == tokenize.COMMENT:
                    comments.append(tok.lstrip("#").strip())
    except Exception:
        pass
    return docstrings + comments

def extract_identifiers(filepath):
    identifiers = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                identifiers.append(node.name)
            elif isinstance(node, ast.ClassDef):
                identifiers.append(node.name)
            elif isinstance(node, ast.Name):
                identifiers.append(node.id)
    except Exception:
        pass
    return identifiers

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9_ ]", " ", text)
    tokens = re.findall(r'\b\w+\b', text)
    return set(tokens)

def compute_jaccard(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

# ---- MAIN ----

def analyze_local_zip(zip_path):
    repo_name = os.path.basename(zip_path).replace(".zip", "")
    print(f"\n📦 Analyzing {repo_name}...")

    repo_path = unzip_repo(zip_path)

    all_doc_text = extract_readme(repo_path)
    all_code_identifiers = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                fpath = os.path.join(root, file)
                all_code_identifiers.extend(extract_identifiers(fpath))
                all_doc_text += " ".join(extract_docstrings_comments(fpath))

    doc_tokens = clean_and_tokenize(all_doc_text)
    code_tokens = clean_and_tokenize(" ".join(all_code_identifiers))

    score = compute_jaccard(doc_tokens, code_tokens)

    print(f"✅ {repo_name} → Shared Vocabulary Score: {score:.4f}")

    shutil.rmtree(repo_path)
    return repo_name, score

def batch_analyze_zip_folder(folder_path):
    results = []
    for file in os.listdir(folder_path):
        if file.endswith(".zip"):
            zip_path = os.path.join(folder_path, file)
            result = analyze_local_zip(zip_path)
            results.append(result)
    return results

# ---- RUN ----

if __name__ == "__main__":
    print("🔍 Starting batch analysis of zipped repositories...")
    final_results = batch_analyze_zip_folder(ZIP_FOLDER)

    print("\n📊 FINAL RESULTS:")
    for name, score in final_results:
        print(f"{name:30} → Jaccard Score: {score:.4f}")
