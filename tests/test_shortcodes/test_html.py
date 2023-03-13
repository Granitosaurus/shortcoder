from textwrap import dedent
from typing import Dict
import pytest
from shortcoder.manager import Shortcoder
from shortcoder.exceptions import InvalidKeywords, ExtraParameters
from shortcoder.shortcodes.html import HtmlKwargShortcode, HtmlPargShortcode
from lxml import etree


class KeywordUrlShortcode(HtmlKwargShortcode):
    def inputs_to_element(self, inputs: Dict[str, str]) -> etree.Element:
        return etree.fromstring(
            '<{root} rel="noopener noreferrer" target="_blank" href="{href}">{text}</{root}>'.format(
                root=self.rootname, **inputs
            )
        )

    def element_to_inputs(self, html: str) -> Dict[str, str]:
        node = etree.fromstring(html)
        return {"href": node.get("href"), "text": node.text}


url_kwarg_shortcode = KeywordUrlShortcode(
    "url",
    inputs={"href": {"reverse": "@href"}, "text": {"reverse": "text()"}},
    template=dedent("""
        <a rel="noopener noreferrer" target="_blank" href="{{ href }}">{{ text }}</a>
    """),
)


def test_html_kwarg_shortcode():
    sh = Shortcoder([url_kwarg_shortcode])
    assert (
        sh.parse("[%url href=foo.jpg text=image %]")
        == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg">image</a>'
    )
    assert (
        sh.parse("[%url text=image href=foo.jpg %]")
        == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg">image</a>'
    )
    assert sh.parse("[%url text=image %]") == '<a rel="noopener noreferrer" target="_blank" href="">image</a>'
    with pytest.raises(InvalidKeywords, match="""shortcode url got unknown keys """):
        sh.parse("[%url src=foo.jpg %]")


def test_html_kwarg_shortcode_reverse():
    sh = Shortcoder([url_kwarg_shortcode])
    assert (
        sh.reverse('<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image</a>')
        == "[%url href=foo.jpg text=image %]"
    )
    assert (
        sh.reverse("""<a href="foo's.jpg" rel="noopener noreferrer" target="_blank">image</a>""")
        == """[%url href="foo's.jpg" text=image %]"""
    )
    assert (
        sh.reverse("""<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image's</a>""")
        == """[%url href=foo.jpg text="image's" %]"""
    )


class PositionalUrlShortcode(HtmlPargShortcode):
    def inputs_to_element(self, inputs: Dict[str, str]) -> etree.Element:
        return etree.fromstring(
            '<{root} rel="noopener noreferrer" target="_blank" href="{href}">{text}</{root}>'.format(
                root=self.rootname, **inputs
            )
        )

    def element_to_inputs(self, html: str) -> Dict[str, str]:
        node = etree.fromstring(html)
        return [node.get("href"), node.text]


url_pos_shortcode = PositionalUrlShortcode("url", inputs=["href", "text"], rootname="a")


def test_html_parg_shortcode():
    sh = Shortcoder([url_pos_shortcode])
    assert sh.parse("[%url foo.jpg image %]") == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg">image</a>'
    assert sh.parse("[%url foo.jpg %]") == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg"/>'
    with pytest.raises(ExtraParameters, match="""shortcode url got 3 parameters when 2 expected"""):
        sh.parse("[%url foo.jpg bar gaz %]")


def test_html_parg_shortcode_reverse():
    sh = Shortcoder([url_pos_shortcode])
    assert (
        sh.reverse('<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image</a>') == "[%url foo.jpg image %]"
    )
    assert (
        sh.reverse("""<a href="foo's.jpg" rel="noopener noreferrer" target="_blank">image</a>""")
        == """[%url "foo's.jpg" image %]"""
    )
    assert (
        sh.reverse("""<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image's</a>""")
        == """[%url foo.jpg "image's" %]"""
    )
