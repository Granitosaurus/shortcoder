from shortcoder.utils import quote, quote_values


def test_quote():
    assert quote("foo's") == '''"foo's"'''
    assert quote('foo"s') == """'foo\"s'"""
    assert quote("foos") == "foos"
    assert quote("foo with space") == '''"foo with space"'''


def test_quote_values():
    vs = ["foo's", 'foo"s', "foos", "foo with space"]
    assert quote_values(vs) == ['"foo\'s"', "'foo\"s'", "foos", '"foo with space"']
