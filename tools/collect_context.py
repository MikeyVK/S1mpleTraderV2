# tools/collect_context.py
import os

# Definieer welke bestanden en mappen je wilt negeren
IGNORE_DIRS = {'.git', '.vscode', '__pycache__', 'venv', '.venv', 'dist', 'build'}
IGNORE_FILES = {'.gitignore', 'collect_context.py'}
# Definieer welke extensies je wilt meenemen
INCLUDE_EXTENSIONS = {'.py', '.yaml', '.yml', '.md', '.txt'}

def collect_project_context(root_dir, output_file):
    """Verzamelt de inhoud van alle relevante bestanden in één tekstbestand."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Filter de te negeren mappen
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

            for filename in filenames:
                if filename in IGNORE_FILES:
                    continue

                if any(filename.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir)
                    
                    outfile.write(f"--- START FILE: {relative_path.replace(os.sep, '/')} ---\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        outfile.write(f"\n--- END FILE: {relative_path.replace(os.sep, '/')} ---\n\n")
                    except Exception as e:
                        outfile.write(f"*** Error reading file: {e} ***\n\n")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_filename = "docs/project_context.txt"
    collect_project_context(project_root, output_filename)
    print(f"Project context collected in: {output_filename}")
