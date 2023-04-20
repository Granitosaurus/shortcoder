"""
Contains base shortcode types
"""
from typing import Dict, List, Optional, Union
from shortcoder.exceptions import InvalidInput, ShortcodeNotReversible
from shortcoder.utils import quote_values


class Input:
    """Container for shortcode input definition"""

    def __init__(self, name: str, xpath: Optional[str] = None, default: Optional[str] = None) -> None:
        self.name = name
        self.xpath = xpath
        self.default = default

    def __repr__(self) -> str:
        return f"Input({self.name}, default={self.default})"


class _Shortcode:
    """Base shortcode class used by all shortcodes"""

    def __init__(self, name: str, inputs: List[Input]) -> None:
        self.name = name
        self.inputs = inputs

    def reverse(self, text: str) -> str:
        """
        reverse shortcode output to original shortcode
        """
        raise ShortcodeNotReversible("Reverse Functionality Not Implemented")

    def _make_shortcode(self, shortcode_kwargs: Dict[str, str]):
        """rejoin values to shortcode"""
        raise NotImplemented("Must be implemented by subclass")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.inputs})"


class KeywordShortcode(_Shortcode):
    """Keyword argument shortcode, e.g. [% shortcode key1=value1 key2=value2 %]"""

    def _make_shortcode(self, shortcode_kwargs: Dict[str, str]):
        shortcode_kwargs = quote_values(shortcode_kwargs)
        return f"[%{self.name} " + " ".join([f"{key}={value}" for key, value in shortcode_kwargs.items() if value]) + " %]"

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        pass

    def reverse(self, text: str) -> str:
        """reverse shortcode output to original shortcode"""
        raise ShortcodeNotReversible("Reverse Functionality Not Implemented")


class PositionalShortcode(_Shortcode):
    """Positional argument shortcode, e.g. [% shortcode value1 value2 %]"""

    def __init__(self, name: str, inputs: List[Input]) -> None:
        _default_allowed = True
        for input in inputs[::-1]:
            if input.default is None:
                _default_allowed = False
            elif not _default_allowed:
                raise InvalidInput(
                    f"Only trailing inputs can have default values: {input.name} has default {input.default} but is not trailing"
                )
        super().__init__(name, inputs)

    def _make_shortcode(self, shortcode_kwargs: Dict[str, str]):
        """turn shortcode values into shortcode string"""
        shortcode_kwargs = quote_values(shortcode_kwargs)
        return f"[%{self.name} " + " ".join(shortcode_kwargs.values()).strip() + " %]"

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        pass

    def reverse(self, text: str) -> str:
        """reverse shortcode output to original shortcode"""
        raise ShortcodeNotReversible("Reverse Functionality Not Implemented")
