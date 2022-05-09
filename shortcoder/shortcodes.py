"""
Contains base shortcode types
"""
import shlex
from typing import Dict, List, Optional, Union
from shortcoder.exceptions import ShotcodeNotReversible


class Shortcode:
    name = NotImplemented

    def reverse(self, text: str) -> str:
        """
        reverse shortcode output to original shortcode
        """
        raise ShotcodeNotReversible("Reverse Functionality Not Implemented")

    def _quote_values(self, values: Union[Dict[str, str], List[str]]):
        """
        quote kwarg or arg values if they need to be quoted, i.e. contain a space in them
        foo bar -> "foo bar"
        foo -> "foo"
        """
        if isinstance(values, Dict):
            return {k: f'"{v}"' if (v and len(shlex.split(v)) > 1) else v for k, v in values.items()}
        return [f'"{v}"' if (v and len(shlex.split(v)) > 1) else v for v in values]

    def _rejoin(self, values: Union[Dict[str, str], List[str]]):
        """
        rejoin values to shortcode
        """
        values = self._quote_values(values)
        if isinstance(values, Dict):
            return f"[%{self.name} " + " ".join([f"{key}={value}" for key, value in values.items() if value]) + " %]"
        return f"[%{self.name} " + " ".join(values) + " %]"


class KwargShortcode(Shortcode):
    name = NotImplemented
    keys = tuple()

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        pass


class PargShortcode(Shortcode):
    name = NotImplemented

    def convert(self, args: List[str], context: Optional[Dict] = None):
        pass
