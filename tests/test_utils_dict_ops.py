"""
Tests for manimlib.utils.dict_ops
"""
import pytest

from manimlib.utils.dict_ops import merge_dicts_recursively


def test_merge_empty():
    assert merge_dicts_recursively() == {}


def test_merge_single():
    d = {"a": 1, "b": 2}
    result = merge_dicts_recursively(d)
    assert result == {"a": 1, "b": 2}


def test_merge_two_non_overlapping():
    d1 = {"a": 1}
    d2 = {"b": 2}
    result = merge_dicts_recursively(d1, d2)
    assert result == {"a": 1, "b": 2}


def test_merge_later_dict_wins():
    d1 = {"a": 1}
    d2 = {"a": 2}
    result = merge_dicts_recursively(d1, d2)
    assert result["a"] == 2


def test_merge_recursive():
    d1 = {"a": {"x": 1, "y": 2}}
    d2 = {"a": {"y": 99, "z": 3}}
    result = merge_dicts_recursively(d1, d2)
    assert result["a"]["x"] == 1
    assert result["a"]["y"] == 99
    assert result["a"]["z"] == 3


def test_merge_nested_overwrite_non_dict():
    d1 = {"a": {"x": 1}}
    d2 = {"a": "string"}
    result = merge_dicts_recursively(d1, d2)
    assert result["a"] == "string"


def test_merge_three_dicts():
    d1 = {"a": 1}
    d2 = {"b": 2}
    d3 = {"c": 3}
    result = merge_dicts_recursively(d1, d2, d3)
    assert result == {"a": 1, "b": 2, "c": 3}
