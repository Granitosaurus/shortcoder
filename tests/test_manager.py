import re
from typing import List, Dict, Optional
from shortcoder.manager import Shortcoder
from shortcoder.shortcodes import KeywordShortcode, PositionalShortcode
from shortcoder.exceptions import UnknownShortcode, NoShortcodesRegistered, DuplicateShortcode 
import pytest
from lxml import etree


class PositionalLink(PositionalShortcode):
    re_reverse = re.compile(r"<a.+?</a>", flags=re.DOTALL)

    def convert(self, args: List[str], context: Dict):
        return '<a href="{}">{}</a>'.format(*args)

    def reverse(self, text: str) -> str:
        def convert(match: re.Match):
            node = etree.fromstring(match.group())
            return self._rejoin([node.get('href'), node.text])

        return self.re_reverse.sub(convert, text)


class KeywordLink(KeywordShortcode):
    re_reverse = re.compile(r"<a.+?</a>", flags=re.DOTALL)

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        return '<a href="{url}">{text}</a>'.format(**kwargs)

    def reverse(self, text: str) -> str:
        def convert(match: re.Match):
            node = etree.fromstring(match.group())
            values = {"url": node.get('href'), "text": node.text}
            return self._rejoin(values)

        return self.re_reverse.sub(convert, text)

positional_link = PositionalLink("link", inputs=["url", "text"])
keyword_link = KeywordLink("link", inputs={"url":"", "text":"default"})

def test_keyword_shortcode():
    sh = Shortcoder([keyword_link])
    assert sh.parse("[%link url=one text=two%]") == '<a href="one">two</a>'
    assert sh.parse("[%link text=two url=one%]") == '<a href="one">two</a>'
    assert sh.parse("""[%link text="two plus" url=one%]""") == '<a href="one">two plus</a>'
    assert sh.parse("""[%link url="one" text="two"%]""") == '<a href="one">two</a>'

    # quotes need to be quoted
    assert sh.parse("""[%link url="one's" text=two%]""") == """<a href="one's">two</a>"""
    with pytest.raises(ValueError, match="No closing quotation"):
        sh.parse("[%link url=one's text=two%]") == '<a href="one">two</a>'

    # reversing
    assert sh.reverse('<a href="one">two</a>') == """[%link url=one text=two %]"""
    # check quoting
    assert sh.reverse("""<a href="one">two's</a>""") == """[%link url=one text="two's" %]"""
    assert sh.reverse("""<a href="one with space">two's</a>""") == """[%link url="one with space" text="two's" %]"""
    assert sh.reverse("""<a href="one">two"s</a>""") == """[%link url=one text='two"s' %]"""
    assert sh.reverse("""<a href="one's">two's</a>""") == """[%link url="one's" text="two's" %]"""


def test_positional_shortcode():
    sh = Shortcoder([positional_link])
    assert sh.parse("[%link one two%]") == '<a href="one">two</a>'

    # check whitespace
    assert sh.parse("[% link one two %]") == '<a href="one">two</a>'
    assert sh.parse("[%link one two %]") == '<a href="one">two</a>'
    assert sh.parse("[% link one two%]") == '<a href="one">two</a>'

    # check quoting
    assert sh.parse('[% link "one" "two" %]') == '<a href="one">two</a>'
    assert sh.parse("[% link 'one' 'two' %]") == '<a href="one">two</a>'

    # shortcode name doesn't allow quoting:
    with pytest.raises(UnknownShortcode, match='[% "link" "one" "two" %]'):
        assert sh.parse('[% "link" "one" "two" %]') == '<a href="one">two</a>'

    # check unknown shortcode raise
    with pytest.raises(UnknownShortcode, match="[%unknown one two %]"):
        assert sh.parse("[%unknown one two %]") == ""

    # reversing
    assert sh.reverse('<a href="one">two</a>') == """[%link one two %]"""
    assert sh.reverse("""<a href="one's">two's</a>""") == """[%link "one's" "two's" %]"""
    assert sh.reverse("""<a href='one"s'>two"s</a>""") == """[%link 'one"s' 'two"s' %]"""


def test_manager_unknown_shortcode():
    sh = Shortcoder([positional_link])
    with pytest.raises(UnknownShortcode):
        assert sh.parse("[%linkz one two %]")



def test_manager_noshortcodes_registered():
    sh = Shortcoder()
    with pytest.raises(NoShortcodesRegistered):
        sh.parse("foobar")


def test_manager_duplicated_registered():
    with pytest.raises(DuplicateShortcode):
        Shortcoder([positional_link, keyword_link])
