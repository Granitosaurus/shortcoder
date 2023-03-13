"""
Contains base shortcode types
"""
from typing import Dict, List, Optional, Union
from shortcoder.exceptions import ShotcodeNotReversible
from shortcoder.utils import quote_values


class Shortcode:
    name = NotImplemented

    def reverse(self, text: str) -> str:
        """
        reverse shortcode output to original shortcode
        """
        raise ShotcodeNotReversible("Reverse Functionality Not Implemented")

    def _rejoin(self, values: Union[Dict[str, str], List[str]]):
        """
        rejoin values to shortcode
        """
        values = quote_values(values)
        if isinstance(values, Dict):
            return f"[%{self.name} " + " ".join([f"{key}={value}" for key, value in values.items() if value]) + " %]"
        return f"[%{self.name} " + " ".join(values).strip() + " %]"


class KeywordShortcode(Shortcode):
    name = NotImplemented
    keys = tuple()

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        pass


class PositionalShortcode(Shortcode):
    name = NotImplemented

    def convert(self, args: List[str], context: Optional[Dict] = None):
        pass
