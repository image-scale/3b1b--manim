"""
Log parser for manimlib pytest output.
Parses pytest verbose output into per-test results.
"""
from __future__ import annotations

import re


def parse_log(log: str) -> dict[str, str]:
    """Parse test runner output into per-test results.

    Args:
        log: Full stdout+stderr output of ``bash run_test.sh 2>&1``.

    Returns:
        Dict mapping test_id to status.
        - test_id: pytest native format, e.g.
          ``tests/foo.py::TestClass::test_func[param]``
        - status: one of "PASSED", "FAILED", "SKIPPED", "ERROR"
    """
    # Strip ANSI escape codes
    log = re.sub(r'\x1b\[[0-9;]*m', '', log)

    results: dict[str, str] = {}

    # Pattern for inline pytest verbose lines:
    # "tests/foo.py::test_bar PASSED                   [ 12%]"
    # Also handles parametrized: "tests/foo.py::test_bar[p1] FAILED  [ 50%]"
    inline_pattern = re.compile(
        r'^(tests/\S+::\S+.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)'
        r'(?:\s.*?)?\s+\[\s*\d+%\]',
        re.MULTILINE,
    )
    for m in inline_pattern.finditer(log):
        test_id = m.group(1).strip()
        status = m.group(2)
        results.setdefault(test_id, status)

    # Pattern for summary lines (appear after the test run):
    # "PASSED tests/foo.py::test_bar"
    # "FAILED tests/foo.py::test_bar - AssertionError"
    summary_pattern = re.compile(
        r'^(PASSED|FAILED|SKIPPED|ERROR)\s+(tests/\S+::\S+)',
        re.MULTILINE,
    )
    for m in summary_pattern.finditer(log):
        status = m.group(1)
        test_id = m.group(2)
        results.setdefault(test_id, status)

    # Collection errors: "ERROR tests/foo.py" (no "::", indicates import failure)
    error_pattern = re.compile(
        r'^ERROR\s+(tests/[^\s:]+\.py)\s*$',
        re.MULTILINE,
    )
    for m in error_pattern.finditer(log):
        results.setdefault(m.group(1), 'ERROR')

    return results


if __name__ == '__main__':
    import sys
    log = open(sys.argv[1] if len(sys.argv) > 1 else 'test_output.log').read()
    r = parse_log(log)
    print(f"Parsed {len(r)} tests")
    dist = {s: sum(1 for v in r.values() if v == s) for s in set(r.values())}
    print(f"Status distribution: {dist}")

