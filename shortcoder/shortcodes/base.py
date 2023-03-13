"""
Contains base shortcode types
"""
from typing import Dict, List, Optional, Union
from shortcoder.exceptions import ShotcodeNotReversible
from shortcoder.utils import quote_values


class Shortcode:
    def reverse(self, text: str) -> str:
        """
        reverse shortcode output to original shortcode
        """
        raise ShotcodeNotReversible("Reverse Functionality Not Implemented")

    def _rejoin(self, values: Union[Dict[str, str], List[str]]):
        """rejoin values to shortcode"""
        return f"[%{self.name} " + " ".join(values).strip() + " %]"


class KeywordShortcode(Shortcode):
    def __init__(self, name: str, inputs: Dict[str, str]) -> None:
        self.name = name
        self.inputs = inputs

    def _rejoin(self, values: Dict[str, str]):
        values = {k: v for k, v in values.items() if v != self.inputs[k]}
        values = quote_values(values)
        return f"[%{self.name} " + " ".join([f"{key}={value}" for key, value in values.items() if value]) + " %]"
    
    def _convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        inputs = {k: kwargs.get(k, v) for k, v in self.inputs.items()}
        return self.convert(inputs, context)

    def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
        pass


class PositionalShortcode(Shortcode):
    def __init__(self, name: str, inputs: List[str]) -> None:
        self.name = name
        self.inputs = inputs

    def _rejoin(self, values: List[str]):
        """rejoin values to shortcode"""
        values = quote_values(values)
        return f"[%{self.name} " + " ".join(values).strip() + " %]"

    def _convert(self, args: List[str], context: Optional[Dict] = None):
        pad_length = len(self.inputs) - len(args)
        args = args + [""] * pad_length
        return self.convert(args, context)

    def convert(self, args: List[str], context: Optional[Dict] = None):
        pass
