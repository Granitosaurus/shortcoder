import re
from typing import Dict, List, Optional

import pytest
from lxml import html

from shortcoder.exceptions import DuplicateShortcode, NoShortcodesRegistered, UnknownShortcode
from shortcoder.manager import Shortcoder
from shortcoder.shortcodes import KeywordShortcode, PositionalShortcode
from shortcoder.shortcodes.base import Input


class PositionalLink(PositionalShortcode):
    re_reverse = re.compile(r"<a.+?</a>", flags=re.DOTALL)

    def convert(self, kwargs: Dict[str, str], context: Dict):
        return '<a href="{url}">{text}</a>'.format(**kwargs)

    def reverse(self, text: str) -> str:
        def convert(match: re.Match):
            node = html.fromstring(match.group())
            return self._make_shortcode({"href": node.get("href"), "text": node.text})

        return self.re_reverse.sub(convert, text)


class KeywordLink(KeywordShortcode):
    re_reverse = re.compile(r"<a.+?</a>", flags=re.DOTALL)

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        return '<a href="{url}">{text}</a>'.format(**kwargs)

    def reverse(self, text: str) -> str:
        def convert(match: re.Match):
            node = html.fromstring(match.group())
            values = {"url": node.get("href"), "text": node.text}
            return self._make_shortcode(values)

        return self.re_reverse.sub(convert, text)




class TestConvert:
    def setup_method(self) -> None:
        keyword_link = KeywordLink("link", inputs=[Input("url"), Input("text")])
        self.sh = Shortcoder([keyword_link])

    def test_keyword_shortcode_order(self):
        assert self.sh.parse("[%link url=one text=two%]") == '<a href="one">two</a>'
        assert self.sh.parse("[%link text=two url=one%]") == '<a href="one">two</a>'

    def test_keyword_shortcode_quotes(self):
        assert self.sh.parse("""[%link text="two plus" url=one%]""") == '<a href="one">two plus</a>'
        assert self.sh.parse("""[%link url="one" text="two"%]""") == '<a href="one">two</a>'

    def test_quoting(self):
        # quotes need to be quoted
        assert self.sh.parse("""[%link url="one's" text=two%]""") == """<a href="one's">two</a>"""
        with pytest.raises(ValueError, match="No closing quotation"):
            self.sh.parse("[%link url=one's text=two%]") == '<a href="one">two</a>'


class TestReverse:
    def setup_method(self) -> None:
        keyword_link = KeywordLink("link", inputs=[Input("url"), Input("text")])
        self.sh = Shortcoder([keyword_link])

    def test_success(self):
        # reversing
        assert self.sh.reverse('<a href="one">two</a>') == """[%link url=one text=two %]"""

    def test_quotes(self):
        # check quoting
        assert self.sh.reverse("""<a href="one">two's</a>""") == """[%link url=one text="two's" %]"""
        assert (
            self.sh.reverse("""<a href="one with space">two's</a>""")
            == """[%link url="one with space" text="two's" %]"""
        )
        assert self.sh.reverse("""<a href="one">two"s</a>""") == """[%link url=one text='two"s' %]"""
        assert self.sh.reverse("""<a href="one's">two's</a>""") == """[%link url="one's" text="two's" %]"""


class TestPositional():
    def setup_method(self) -> None:
        positional_link = PositionalLink("link", inputs=[Input("url"), Input("text")])
        self.sh = Shortcoder([positional_link])


    def test_positional_shortcode(self):
        assert self.sh.parse("[%link one two%]") == '<a href="one">two</a>'

    def test_whitespace(self):
        assert self.sh.parse("[% link one two %]") == '<a href="one">two</a>'
        assert self.sh.parse("[%link one two %]") == '<a href="one">two</a>'
        assert self.sh.parse("[% link one two%]") == '<a href="one">two</a>'
    
    def test_quoting(self):
        assert self.sh.parse('[% link "one" "two" %]') == '<a href="one">two</a>'
        assert self.sh.parse("[% link 'one' 'two' %]") == '<a href="one">two</a>'

        # shortcode name doesn't allow quoting:
        with pytest.raises(UnknownShortcode, match='[% "link" "one" "two" %]'):
            assert self.sh.parse('[% "link" "one" "two" %]') == '<a href="one">two</a>'

    def test_unknown_shortcode(self): 
        # check unknown shortcode raise
        with pytest.raises(UnknownShortcode, match="[%unknown one two %]"):
            assert self.sh.parse("[%unknown one two %]") == ""

    def test_reversing(self):
        assert self.sh.reverse('<a href="one">two</a>') == """[%link one two %]"""
        assert self.sh.reverse("""<a href="one's">two's</a>""") == """[%link "one's" "two's" %]"""
        assert self.sh.reverse("""<a href='one"s'>two"s</a>""") == """[%link 'one"s' 'two"s' %]"""


def test_manager_unknown_shortcode():
    positional_link = PositionalLink("link", inputs=[Input("url"), Input("text")])
    sh = Shortcoder([positional_link])
    with pytest.raises(UnknownShortcode):
        assert sh.parse("[%linkz one two %]")


def test_manager_noshortcodes_registered():
    sh = Shortcoder()
    with pytest.raises(NoShortcodesRegistered):
        sh.parse("foobar")


def test_manager_duplicated_registered():

    positional_link = PositionalLink("link", inputs=[Input("url"), Input("text")])
    positional_link2 = PositionalLink("link", inputs=[Input("url"), Input("text")])
    with pytest.raises(DuplicateShortcode):
        Shortcoder([positional_link, positional_link2])
