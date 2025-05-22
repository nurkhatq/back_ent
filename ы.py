import os

# Каталоги и файлы, которые нужно исключить
EXCLUDED_DIRS = {
    'node_modules', '.next', '.git', '__pycache__', '.venv', 'venv', 'env', '.idea', '.DS_Store', '.pytest_cache',
    '.mypy_cache', 'dist', 'build', 'staticfiles'
}
EXCLUDED_FILES = {'.env', '.gitignore', 'package-lock.json', 'yarn.lock', 'requirements.txt'}

def print_directory_structure(root_dir, indent=''):
    entries = sorted(os.listdir(root_dir))
    for entry in entries:
        full_path = os.path.join(root_dir, entry)
        # Пропускаем исключенные файлы и директории
        if entry in EXCLUDED_DIRS or entry in EXCLUDED_FILES:
            continue
        if os.path.isdir(full_path):
            print(f"{indent}📁 {entry}/")
            print_directory_structure(full_path, indent + '    ')
        elif os.path.isfile(full_path):
            print(f"{indent}📄 {entry}")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"📂 Проект: {os.path.basename(base_path)}")
    print_directory_structure(base_path)
