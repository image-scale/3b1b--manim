"""
Smoke tests: verify manimlib submodules import without errors.
"""
import pytest


def test_import_utils_bezier():
    import manimlib.utils.bezier  # noqa: F401


def test_import_utils_color():
    import manimlib.utils.color  # noqa: F401


def test_import_utils_space_ops():
    import manimlib.utils.space_ops  # noqa: F401


def test_import_utils_iterables():
    import manimlib.utils.iterables  # noqa: F401


def test_import_utils_rate_functions():
    import manimlib.utils.rate_functions  # noqa: F401


def test_import_utils_simple_functions():
    import manimlib.utils.simple_functions  # noqa: F401


def test_import_utils_dict_ops():
    import manimlib.utils.dict_ops  # noqa: F401


def test_import_utils_paths():
    import manimlib.utils.paths  # noqa: F401


def test_import_constants():
    import manimlib.constants  # noqa: F401


def test_import_config():
    import manimlib.config  # noqa: F401
