"""
Tests for manimlib.utils.iterables
"""
import pytest

from manimlib.utils.iterables import (
    remove_list_redundancies, list_update, list_difference_update,
    adjacent_pairs, adjacent_n_tuples, batch_by_property,
)


def test_remove_list_redundancies_basic():
    result = remove_list_redundancies([1, 2, 3, 2, 1])
    # Keeps last occurrence of each element
    assert 1 in result
    assert 2 in result
    assert 3 in result
    assert len(result) == 3


def test_remove_list_redundancies_empty():
    assert remove_list_redundancies([]) == []


def test_remove_list_redundancies_no_dupes():
    result = remove_list_redundancies([1, 2, 3])
    assert result == [1, 2, 3]


def test_list_update_combines():
    result = list_update([1, 2, 3], [3, 4, 5])
    assert set(result) == {1, 2, 3, 4, 5}


def test_list_difference_update():
    result = list_difference_update([1, 2, 3, 4], [2, 4])
    assert result == [1, 3]


def test_adjacent_pairs_basic():
    pairs = list(adjacent_pairs([1, 2, 3]))
    assert (1, 2) in pairs
    assert (2, 3) in pairs
    assert (3, 1) in pairs


def test_adjacent_pairs_length():
    items = [10, 20, 30, 40]
    pairs = list(adjacent_pairs(items))
    assert len(pairs) == 4


def test_adjacent_n_tuples_triples():
    triples = list(adjacent_n_tuples([1, 2, 3, 4], 3))
    assert len(triples) == 4
    assert triples[0] == (1, 2, 3)


def test_batch_by_property():
    items = [1, 2, 3, 4, 5, 6]
    batches = list(batch_by_property(items, lambda x: x % 3))
    # Should group consecutive items with the same property
    assert len(batches) > 0
