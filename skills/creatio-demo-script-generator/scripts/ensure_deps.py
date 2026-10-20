"""Make sure the Python libraries the skill needs are installed — run once at the start of every run.

Usage:
    python ensure_deps.py

Checks python-docx, openpyxl and pymupdf; installs only the missing ones with pip (user install), so a
colleague never has to run pip by hand. Prints one line per library. Exit code 1 only if an install failed.
"""
import importlib
import subprocess
import sys

NEEDED = {"docx": "python-docx>=1.1", "openpyxl": "openpyxl>=3.1", "pymupdf": "pymupdf>=1.24"}


def main():
    if sys.version_info < (3, 10):
        print(f"Python {sys.version.split()[0]} is too old — install Python 3.10 or newer from python.org")
        sys.exit(1)
    missing = []
    for module, pkg in NEEDED.items():
        try:
            importlib.import_module(module)
            print(f"ok       {pkg}")
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    print("installing: " + ", ".join(missing))
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--quiet", *missing])
    if r.returncode != 0:
        print("pip install failed — run it by hand: python -m pip install " + " ".join(missing))
        sys.exit(1)
    print("installed")


if __name__ == "__main__":
    main()
