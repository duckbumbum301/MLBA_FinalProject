import os
import sys
import shutil

EXCLUDE_DIRS = {"__pycache__", ".git", ".idea"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".DS_Store"}


def should_skip_dir(dirname: str) -> bool:
    return dirname in EXCLUDE_DIRS


def should_skip_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext in EXCLUDE_EXTS


def copy_tree(src_root: str, dst_root: str) -> None:
    for root, dirs, files in os.walk(src_root):
        # Compute relative path from source root
        rel = os.path.relpath(root, src_root)
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]

        # Ensure destination directory exists
        dst_dir = os.path.join(dst_root, rel) if rel != "." else dst_root
        os.makedirs(dst_dir, exist_ok=True)

        # Copy files
        for f in files:
            if should_skip_file(f):
                continue
            src_path = os.path.join(root, f)
            dst_path = os.path.join(dst_dir, f)
            shutil.copy2(src_path, dst_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/sync_to_pycharm.py <PyCharm project root path>")
        sys.exit(1)

    dst_root = os.path.abspath(sys.argv[1])
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if not os.path.exists(dst_root):
        print(f"Destination does not exist, creating: {dst_root}")
        os.makedirs(dst_root, exist_ok=True)

    print(f"Syncing from: {src_root}")
    print(f"To:          {dst_root}")
    copy_tree(src_root, dst_root)
    print("Done.")


if __name__ == "__main__":
    main()

