"""
Tests for manimlib.utils.simple_functions
"""
import math
import numpy as np
import pytest

from manimlib.utils.simple_functions import (
    sigmoid, choose, clip, arr_clip,
)


def test_sigmoid_zero():
    assert sigmoid(0) == pytest.approx(0.5)


def test_sigmoid_positive():
    val = sigmoid(10.0)
    assert 0.99 < val < 1.0


def test_sigmoid_negative():
    val = sigmoid(-10.0)
    assert 0.0 < val < 0.01


def test_sigmoid_array():
    arr = sigmoid(np.array([-1.0, 0.0, 1.0]))
    assert arr.shape == (3,)
    assert arr[1] == pytest.approx(0.5)


def test_choose_basic():
    assert choose(5, 0) == 1
    assert choose(5, 1) == 5
    assert choose(5, 2) == 10
    assert choose(5, 5) == 1


def test_choose_zero():
    assert choose(0, 0) == 1


def test_clip_below():
    assert clip(1.0, 2.0, 5.0) == 2.0


def test_clip_above():
    assert clip(10.0, 2.0, 5.0) == 5.0


def test_clip_inside():
    assert clip(3.0, 2.0, 5.0) == 3.0


def test_arr_clip():
    arr = np.array([0.0, 5.0, 10.0])
    arr_clip(arr, 2.0, 8.0)
    assert arr[0] == 2.0
    assert arr[1] == 5.0
    assert arr[2] == 8.0
