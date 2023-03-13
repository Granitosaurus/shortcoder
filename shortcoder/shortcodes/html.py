import re
from typing import Dict, List, Optional
from shortcoder.shortcodes.base import PositionalShortcode, KeywordShortcode

try:
    from lxml import etree
except ImportError:
    etree = None


class HtmlPargShortcode(PositionalShortcode):
    def __init__(self, name, inputs: List[str], rootname):
        super().__init__(name=name, inputs=inputs)
        self.rootname = rootname
        self.re_reverse = re.compile(
            rf"<{self.rootname}\b[^>]*>(.*?)</{self.rootname}>", flags=re.IGNORECASE | re.DOTALL
        )
        if not etree:
            raise ImportError("lxml package is required for HtmlShortcode; try: pip install lxml")

    def convert(self, args: List[str], context: Optional[Dict] = None):
        inputs = {k: args[i] for i, k in enumerate(self.inputs)}
        return etree.tostring(self.inputs_to_element(inputs), encoding="unicode")

    def inputs_to_element(self, inputs: Dict[str, str]) -> etree.Element:
        """create html element from input keywords"""
        return etree.fromstring("<{root}>{text}</{root}>".format(root=self.rootname, **inputs))

    def reverse(self, text: str) -> str:
        """returns img shortcode from"""

        def convert(match: re.Match):
            return self._rejoin(self.element_to_inputs(match.group()))

        return self.re_reverse.sub(convert, text)

    def element_to_inputs(self, html: str) -> List[str]:
        """create input keywords from html element"""
        raise NotImplementedError()


class HtmlKwargShortcode(KeywordShortcode):
    def __init__(self, name, inputs: Dict[str, str], rootname):
        super().__init__(name=name, inputs=inputs)
        if not etree:
            raise ImportError("lxml package is required for HtmlShortcode; try: pip install lxml")
        self.rootname = rootname
        self.re_reverse = re.compile(
            rf"(<{self.rootname}\b[^>]*>.*?</{self.rootname}>)", flags=re.IGNORECASE | re.DOTALL
        )

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None) -> str:
        inputs = {k: kwargs.get(k, v) for k, v in self.inputs.items()}
        return etree.tostring(self.inputs_to_element(inputs), encoding="unicode")

    def inputs_to_element(self, inputs: Dict[str, str]) -> etree.Element:
        """create html element from input keywords"""
        return etree.fromstring("<{root}>{text}</{root}>".format(root=self.rootname, **inputs))

    def reverse(self, text: str) -> str:
        """returns img shortcode from"""

        def convert(match: re.Match):
            return self._rejoin(self.element_to_inputs(match.group()))

        result = self.re_reverse.sub(convert, text)
        return result

    def element_to_inputs(self, html: str) -> Dict[str, str]:
        """create input keywords from html element"""
        raise NotImplementedError()
