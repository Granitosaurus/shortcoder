import re
from typing import Callable, Dict, List, Optional

from shortcoder.exceptions import RenderingError, ShortcodeNotReversible
from shortcoder.shortcodes.base import Input, KeywordShortcode, PositionalShortcode

try:
    from lxml import html
except ImportError:
    html = None


class HTMLMixin:
    re_reverse = re.compile(r"(<[^/]*?\b[^>]*>.*?</.*?>)", flags=re.IGNORECASE | re.DOTALL)

    def __init__(self, name, inputs: List[Input], template: Callable | str, class_: Optional[str] = None):
        super().__init__(name, inputs)
        if not html:
            raise ImportError("lxml package is required for HtmlShortcode; try: pip install lxml")
        if isinstance(template, str):
            self.template = template.format
        else:
            self.template = template
        self.class_ = class_ or f"shortcode-{name}"

    def _handle_lxml_errors(self, exception: Exception):
        if isinstance(exception, ValueError):
            if "Unicode strings with encoding declartion are not supported" in ''.join(exception.args):
                return
        return exception

    def reverse(self, text: str) -> str:
        """Reverse text value to shortcode"""

        def convert(match: re.Match):
            if not match.group():
                return match.group()
            try:
                tree = html.fromstring(match.group())
            except Exception as e:
                if new_exception:=self._handle_lxml_errors(e):
                    raise new_exception
                else:
                    return match.group()
            if self.class_ not in tree.get("class", "").split(" "):
                return match.group()
            shortcode_kwargs = {}
            for inp in self.inputs:
                if not inp.xpath:
                    raise ShortcodeNotReversible(f"shortcode {self.name} input {inp} is missing reversing instructions {inp.xpath=}")
                shortcode_kwargs[inp.name] = tree.xpath(inp.xpath)[0] or ""
            if shortcode_kwargs:
                return self._make_shortcode(shortcode_kwargs)
            return match.group()

        result = self.re_reverse.sub(convert, text)
        return result

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None) -> str:
        inputs = {}
        for input in self.inputs:
            value = kwargs.get(input.name, input.default)
            if value is None:
                raise RenderingError(f"Missing required input {input.name} for {self.name} shortcode; {kwargs=}")
            inputs[input.name] = value or ""
        try:
            html_text = self.template(**inputs, context=context, shortcode=self)
            tree = html.fromstring(html_text)
            _classes = tree.get("class", "").split(" ") + [self.class_]
            tree.set("class", " ".join(_classes).strip())
        except Exception as e:
            raise RenderingError(f"Error rendering {self.name} {kwargs=} shortcode: {e}", e)
        return html.tostring(tree, encoding="unicode")


class HtmlPargShortcode(HTMLMixin, PositionalShortcode):
    pass


class HtmlKwargShortcode(HTMLMixin, KeywordShortcode):
    pass
