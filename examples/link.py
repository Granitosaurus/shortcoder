import re
from typing import Dict, Optional
from urllib.parse import urljoin
from shortcoder.shortcodes import KwargShortcode
from parsel import Selector


class LinkShortcode(KwargShortcode):
    """
    html image shortcode:
    [%url href="foo.jpg" text="bar"%]
    ↪<a href="foo.jpg">bar</a>
    [%url href="foo"%]
    ↪<a href="foo.jpg">foo.jpg</a>

    If urlbase is provided:
    urlbase = "https://scrapecrow.com"
    [%url href="foo.jpg"%]
    ↪<a href="https://scrapecrow.com/foo.jpg">https://scrapecrow.com/foo.jpg</a>
    [%url href="foo.jpg" text="bar"%]
    ↪<a href="https://scrapecrow.com/foo.jpg">bar</a>
    """

    name = "url"
    re_reverse = re.compile(r"<a.+?</a>", flags=re.DOTALL)
    keys = ("href", "text", "rel")

    def __init__(self, urlbase: str = "", rel: str = ""):
        super().__init__()
        self.urlbase = urlbase
        self.rel = rel

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        href = urljoin(self.urlbase, kwargs["href"])
        text = kwargs.get("text", "") or href
        rel = kwargs.get("rel", "") or " ".join(self.rel)
        return f'<a rel="{rel}" href="{href}">{text or href}</a>'.replace(' rel=""', "")

    def reverse(self, text: str) -> str:
        """returns img shortcode from"""

        def convert(match: re.Match):
            sel = Selector(match.group())
            node = sel.xpath("body/a")[0]
            data = {
                "href": node.xpath("@href").get(),
                "text": node.xpath("text()").get(""),
                "rel": node.xpath("@rel").get(),
            }
            if data["rel"] == self.rel:
                data["rel"] = None
            if data["text"] == data["href"]:
                data["text"] = None
            return self._rejoin(data)

        return self.re_reverse.sub(convert, text)


def test_LinkShortcode():
    assert LinkShortcode().convert({"href": "123.jpg"}) == '<a href="123.jpg">123.jpg</a>'
    assert LinkShortcode().convert({"href": "123.jpg", "text": "click here"}) == '<a href="123.jpg">click here</a>'
    assert LinkShortcode().reverse('<a href="123.jpg">click here</a>')
    assert (
        LinkShortcode().reverse('<a href="123.jpg" rel="noopener noreferrer">click here</a>')
        == '[%url href=123.jpg text="click here" rel="noopener noreferrer" %]'
    )
    assert LinkShortcode().reverse('<a href="123.jpg">123.jpg</a>') == "[%url href=123.jpg %]"


if __name__ == "__main__":
    test_LinkShortcode()
