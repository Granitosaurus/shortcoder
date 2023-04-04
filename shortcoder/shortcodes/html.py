import re
from itertools import zip_longest
from typing import Callable, Dict, List, Optional

from shortcoder.exceptions import RenderingError
from shortcoder.shortcodes.base import Input, KeywordShortcode, PositionalShortcode

try:
    from lxml import etree
except ImportError:
    etree = None


class HTMLMixin:
    re_reverse = re.compile(r"(<.*?\b[^>]*>.*?</.*?>)", flags=re.IGNORECASE | re.DOTALL)

    def __init__(self, name, inputs: List[Input], template: Callable | str, class_: Optional[str] = None):
        super().__init__(name, inputs)
        if not etree:
            raise ImportError("lxml package is required for HtmlShortcode; try: pip install lxml")
        if isinstance(template, str):
            self.template = template.format
        else:
            self.template = template
        self.class_ = class_ or f"shortcode-{name}"

    def reverse(self, text: str) -> str:
        """Reverse text value to shortcode"""

        def convert(match: re.Match):
            tree = etree.fromstring(match.group())
            if self.class_ not in tree.get("class", "").split(" "):
                return match.group()
            inputs = {}
            for inp in self.inputs:
                inputs[inp.name] = tree.xpath(inp.xpath)[0] or ""
            if inputs:
                return self._make_shortcode(inputs)
            return match.group()

        result = self.re_reverse.sub(convert, text)
        return result


class HtmlPargShortcode(HTMLMixin, PositionalShortcode):
    def convert(self, args: List[str], context: Optional[Dict] = None) -> str:
        inputs = {k: v or "" for k, v in zip_longest(self.inputs, args)}
        try:
            html = self.template(**inputs)
            tree = etree.fromstring(html)
            _classes = tree.get("class", "").split(" ") + [self.class_]
            tree.set("class", " ".join(_classes).strip())
        except Exception as e:
            raise RenderingError(f"Error rendering {self.name} shortcode: {e}", e)
        return etree.tostring(tree, encoding="unicode")


class HtmlKwargShortcode(HTMLMixin, KeywordShortcode):
    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None) -> str:
        inputs = {}
        for input in self.inputs:
            value = kwargs.get(input.name, input.default)
            if input.required and not value:
                raise RenderingError(f"Missing required input {input.name} for {self.name} shortcode; {kwargs=}")
            inputs[input.name] = value or ""
        try:
            html = self.template(**inputs)
            # add shortcode class to root node
            tree = etree.fromstring(html)
            _classes = tree.get("class", "").split(" ") + [self.class_]
            tree.set("class", " ".join(_classes).strip())
        except Exception as e:
            raise RenderingError(f"Error rendering {self.name} shortcode: {e}", e)
        return etree.tostring(tree, encoding="unicode")
