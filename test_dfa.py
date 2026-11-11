import pytest
from dfa import DFA, EXAMPLES, all_strings, divisible_by_3, ends_with_01, no_two_ones


def test_divisible_by_3_matches_python():
    d = divisible_by_3()
    for s in all_strings("01", 12):
        expected = (int(s, 2) % 3 == 0) if s else True    # empty string counts as 0
        assert d.accepts(s) == expected, s


def test_ends_with_01_matches_python():
    d = ends_with_01()
    for s in all_strings("01", 12):
        assert d.accepts(s) == s.endswith("01"), s


def test_no_two_ones_matches_python():
    d = no_two_ones()
    for s in all_strings("01", 12):
        assert d.accepts(s) == ("11" not in s), s


def test_trace_is_correct():
    ok, trace = ends_with_01().run("101")
    assert ok and trace == [("q0", "1", "q0"), ("q0", "0", "q1"), ("q1", "1", "q2")]


def test_missing_transition_is_rejected():
    with pytest.raises(ValueError):
        DFA("bad", "", ["a", "b"], "01", "a", ["b"], {("a", "0"): "b", ("a", "1"): "a", ("b", "0"): "a"})


def test_bad_symbol_is_rejected():
    with pytest.raises(ValueError):
        ends_with_01().run("012")


def test_unreachable_state_found():
    t = {("a", "0"): "a", ("a", "1"): "a", ("z", "0"): "a", ("z", "1"): "a"}
    d = DFA("x", "", ["a", "z"], "01", "a", ["a"], t)
    assert d.unreachable_states() == ["z"]


def test_examples_have_no_unreachable_states():
    for make in EXAMPLES:
        assert make().unreachable_states() == []
