import re
import shlex
from typing import List, Dict
from shortcoder.exceptions import (
    DuplicateShortcode,
    InvalidKeywords,
    ExtraParameters,
    NoShortcodesRegistered,
    UnknownShortcode,
)
from shortcoder.shortcodes.base import _Shortcode, KeywordShortcode, PositionalShortcode


class Shortcoder:
    default_shortcodes = tuple()
    re_shcode = re.compile(r"\[%\s*(\S+)(.+?)%\]", re.DOTALL)

    def __init__(self, shortcodes: List[_Shortcode] = None, context: Dict = None) -> None:
        """
        Shortcode parser

        Parameters
        ----------
        shortcodes : List[Shortcode], optional
            List of shortcodes to register on init
        context : Dict, optional
            any extra context that will be passed to every shortcode conversion
        """
        self.shortcodes = {}
        for shortcode in shortcodes or self.default_shortcodes:
            self.register(shortcode)
        self.context = context or {}

    def register(self, shortcode: _Shortcode):
        """
        register a shortcode to the current parser object

        Parameters
        ----------
        shortcode
            Any shortcode object

        Raises
        ------
        DuplicateShortcode
            raised if shortcode name already exists
        """
        if shortcode.name in self.shortcodes:
            raise DuplicateShortcode(f"{shortcode.name} already registered")
        self.shortcodes[shortcode.name] = shortcode

    def parse(self, text: str, context=None) -> str:
        """
        parse text and convert shortcodes to their convert values

        Parameters
        ----------
        text
            text to parse
        context
            extra context to pass to shortcode.convert method. If not supplied self.context will be used

        Returns
        -------
        text
            converted text

        Raises
        ------
        NoShortcodesRegistered
            raised when manager has no shortcodes registered
        UnknownShortcode
            raised when unknown shortcode is encountered
        UnknownShortcodeKey
            raised when kwarg shortcode encounters unknown key
        """
        if not self.shortcodes:
            raise NoShortcodesRegistered
        if not context:
            context = self.context

        def convert(match: re.Match):
            name, args = match.groups()
            try:
                handler = self.shortcodes[name]
            except KeyError:
                raise UnknownShortcode(name, match.group())
            args = shlex.split(args.strip())
            if isinstance(handler, PositionalShortcode):
                kwargs = {}
                for i, arg in enumerate(args):
                    try:
                        kwargs[handler.inputs[i].name] = arg
                    except IndexError:
                        raise ExtraParameters(
                            "shortcode {name} got {count} parameters when {exp} expected ".format(
                                name=name,
                                count=len(args),
                                exp=len(handler.inputs),
                            )
                        )
                return handler.convert(kwargs, context=context)
            elif isinstance(handler, KeywordShortcode):
                kwargs = {}
                for i, arg in enumerate(args):
                    key, value = arg.split("=", 1)
                    kwargs[key] = value
                _input_names = [i.name for i in handler.inputs]
                invalid = [key for key in kwargs if key not in _input_names]
                if invalid:
                    raise InvalidKeywords(
                        "shortcode {name} got unknown keys {keys}, allowed: {inputs}".format(
                            name=name,
                            keys=invalid,
                            inputs=handler.inputs,
                        )
                    )
                return handler.convert(kwargs, context=context)

        result = self.re_shcode.sub(convert, text)
        return result
    
    def find_shortcodes(self, text: str) -> List[str]:
        """
        Find all shortcodes in text

        Parameters
        ----------
        text
            text to search

        Returns
        -------
        List[str]
            list of shortcodes found
        """
        return self.re_shcode.findall(text)

    def reverse(self, text: str) -> str:
        """
        Reverse shortcode value to shortcode if possible
        """
        for code in self.shortcodes.values():
            text = code.reverse(text)
        return text
