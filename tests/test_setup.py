import sys


def test_python_version() -> None:
    """Python 3.11+ is required by the project."""
    assert sys.version_info >= (3, 11), f"Required Python 3.11+, got {sys.version}"
