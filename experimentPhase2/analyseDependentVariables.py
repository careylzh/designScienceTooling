import os
import zipfile
import tempfile
import shutil
import json
import re
import math
import statistics
from collections import Counter
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from pylint import epylint as lint
from nltk.tokenize import word_tokenize
import textstat
import subprocess

# Make sure NLTK is ready
import nltk
nltk.download('punkt')

def extract_zip_files(zip_folder):
    extracted_paths = []
    for file in os.listdir(zip_folder):
        if file.endswith('.zip'):
            full_path = os.path.join(zip_folder, file)
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            extracted_paths.append((file, temp_dir))
    return extracted_paths

def get_python_files(repo_path):
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(repo_path) for f in filenames if f.endswith('.py')]

def calculate_cyclomatic_complexity(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        blocks = cc_visit(code)
        return sum(b.complexity for b in blocks), len(blocks)
    except:
        return 0, 0

def calculate_maintainability_index(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        return mi_visit(code, False)
    except:
        return 0.0

def extract_identifiers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        return re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', code)
    except:
        return []

def naming_convention_stats(identifiers):
    snake_case = sum(1 for i in identifiers if re.match(r'^[a-z]+(_[a-z0-9]+)*$', i))
    camel_case = sum(1 for i in identifiers if re.match(r'^[a-z]+([A-Z][a-z0-9]*)+$', i))
    pascal_case = sum(1 for i in identifiers if re.match(r'^[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)*$', i))
    total = len(identifiers)
    if total == 0:
        return {"snake_case": 0, "camel_case": 0, "pascal_case": 0, "entropy": 0, "std_dev": 0}
    entropy = -sum((c / total) * math.log2(c / total) for c in [snake_case, camel_case, pascal_case] if c > 0)
    std_dev = statistics.pstdev([snake_case, camel_case, pascal_case])
    return {"snake_case": snake_case, "camel_case": camel_case, "pascal_case": pascal_case, "entropy": entropy, "std_dev": std_dev}


def run_pylint(file_path):
    try:
        result = subprocess.run(
            ['pylint', '--disable=R,C', file_path],
            capture_output=True,
            text=True
        )
        output = result.stdout
        warnings = len(re.findall(r'\b[RCWEF]:\s', output))
        return warnings
    except Exception as e:
        print(f"Failed to run pylint on {file_path}: {e}")
        return 0


def get_comment_density(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        return comment_lines / len(lines) if lines else 0
    except:
        return 0

def get_readability_of_comments(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        comments = [line.strip()[1:].strip() for line in lines if line.strip().startswith('#')]
        text = ' '.join(comments)
        return textstat.flesch_reading_ease(text) if text else 0
    except:
        return 0

def analyze_repo(repo_path):
    print(f"Analyzing repository at {repo_path}...")
    py_files = get_python_files(repo_path)

    total_complexity, total_blocks = 0, 0
    maintainability_scores = []
    identifiers = []
    total_warnings = 0
    comment_densities = []
    readability_scores = []
    print(f"Found {len(py_files)} Python files.")
    for file in py_files:
        print(f"Analyzing {file}...")
        complexity, blocks = calculate_cyclomatic_complexity(file)
        total_complexity += complexity
        total_blocks += blocks

        maintainability_scores.append(calculate_maintainability_index(file))
        identifiers.extend(extract_identifiers(file))
        print(f"Extracted {len(identifiers)} identifiers from {file}.")
        total_warnings += run_pylint(file)
        comment_densities.append(get_comment_density(file))
        readability_scores.append(get_readability_of_comments(file))
        print(f"Comment density: {comment_densities[-1]}, Readability score: {readability_scores[-1]}")
    print(f"Total cyclomatic complexity: {total_complexity}, Total blocks: {total_blocks}")
    if not py_files:
        return None

    naming_stats = naming_convention_stats(identifiers)

    return {
        "cyclomatic_complexity_avg": total_complexity / total_blocks if total_blocks else 0,
        "maintainability_index_avg": sum(maintainability_scores) / len(maintainability_scores),
        "naming_stats": naming_stats,
        "pylint_warning_count": total_warnings,
        "comment_density_avg": sum(comment_densities) / len(comment_densities),
        "readability_score_avg": sum(readability_scores) / len(readability_scores)
    }

def analyze_zip_folder(zip_folder):
    results = {}
    extracted_repos = extract_zip_files(zip_folder)

    for filename, path in extracted_repos:
        print(f"Analyzing {filename}...")
        result = analyze_repo(path)
        results[filename] = result
        shutil.rmtree(path)  # Clean up extracted files

    return results

# Example usage:
if __name__ == "__main__":
    zip_input_folder = '../zipped_repos'  # <-- change this
    output_file = 'repo_analysis_results.json'

    analysis_results = analyze_zip_folder(zip_input_folder)

    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)

    print(f"Saved results to {output_file}")
