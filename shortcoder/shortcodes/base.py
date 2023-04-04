"""
Contains base shortcode types
"""
from typing import Dict, List, Optional, Union
from shortcoder.exceptions import InvalidInput, ShotcodeNotReversible
from shortcoder.utils import quote_values


class Input:
    """Container for shortcode input definition"""

    def __init__(
        self, name: str, xpath: Optional[str] = None, default: Optional[str] = None, required: bool = False
    ) -> None:
        self.name = name
        self.xpath = xpath
        self.default = default
        self.required = required

    def __repr__(self) -> str:
        return f"Input({self.name})"


class _Shortcode:
    """Base shortcode class used by all shortcodes"""

    def __init__(self, name: str, inputs: List[Input]) -> None:
        self.name = name
        self.inputs = inputs

    def reverse(self, text: str) -> str:
        """
        reverse shortcode output to original shortcode
        """
        raise ShotcodeNotReversible("Reverse Functionality Not Implemented")

    def _make_shortcode(self, values: Union[Dict[str, str], List[str]]):
        """rejoin values to shortcode"""
        return f"[%{self.name} " + " ".join(values).strip() + " %]"


class KeywordShortcode(_Shortcode):
    """Keyword argument shortcode, e.g. [% shortcode key1=value1 key2=value2 %]"""

    def _make_shortcode(self, values: Dict[str, str]):
        values = quote_values(values)
        return f"[%{self.name} " + " ".join([f"{key}={value}" for key, value in values.items() if value]) + " %]"

    def _convert_with_defaults(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        inputs = {input.name: kwargs.get(input.name, input.default) or "" for input in self.inputs}
        return self.convert(inputs, context)

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        pass

    def reverse(self, text: str) -> str:
        """reverse shortcode output to original shortcode"""
        raise ShotcodeNotReversible("Reverse Functionality Not Implemented")


class PositionalShortcode(_Shortcode):
    """Positional argument shortcode, e.g. [% shortcode value1 value2 %]"""

    def __init__(self, name: str, inputs: List[Input]) -> None:
        for input in inputs:
            if input.default:
                raise InvalidInput(
                    f"Positional shortcodes do not support default values: {input.name} has default {input.default}"
                )
        super().__init__(name, inputs)

    def _make_shortcode(self, values: Dict[str, str]):
        """turn shortcode values into shortcode string"""
        values = quote_values(values)
        return f"[%{self.name} " + " ".join(values.values()).strip() + " %]"

    def _convert_with_defaults(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        inputs = {input.name: kwargs.get(input.name, input.default) or "" for input in self.inputs}
        return self.convert(inputs, context)

    def convert(self, args: List[str], context: Optional[Dict] = None):
        pass

    def reverse(self, text: str) -> str:
        """reverse shortcode output to original shortcode"""
        raise ShotcodeNotReversible("Reverse Functionality Not Implemented")
