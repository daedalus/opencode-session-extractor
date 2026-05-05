"""Hashing and file collision detection utilities for openode_session_extractor."""

import hashlib
import os


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file.

    Args:
        filepath: Path to the file to hash.

    Returns:
        Hex string of SHA-256 hash.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.

    Example:
        >>> compute_file_hash("/tmp/test.txt")
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of string content.

    Args:
        content: String content to hash.

    Returns:
        Hex string of SHA-256 hash.

    Example:
        >>> compute_content_hash("hello")
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_if_changed(output_path: str, content: str) -> bool:
    """Session collision handling based on hash comparison.

    Implements the following logic:
    - If hash(file_on_disk) == hash(content): data = [] (no write, return False)
    - If len(content_in_RAM) > len(content_on_disk): write file
    - Otherwise: skip, return False

    Args:
        output_path: Path to output file.
        content: Content to write.

    Returns:
        True if file was written, False if skipped (hash match or smaller content).

    Example:
        >>> write_if_changed("/tmp/test.txt", "content")
        True
    """
    if os.path.exists(output_path):
        existing_hash = compute_file_hash(output_path)
        new_hash = compute_content_hash(content)

        if existing_hash == new_hash:
            return False  # hashes equal, data = []

        # Hashes differ - check if RAM content is larger
        disk_content_len = os.path.getsize(output_path)
        if len(content) > disk_content_len:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    # New file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True
