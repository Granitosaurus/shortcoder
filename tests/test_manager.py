from typing import List, Dict, Optional
from shortcoder.manager import Shortcoder
from shortcoder.shortcodes import KwargShortcode, PargShortcode, Shortcode
from shortcoder.exceptions import UnknownShortcode, NoShortcodesRegistered, DuplicateShortcode, UnknownShortcodeKey
import pytest


class BasicShortcode(PargShortcode):
    name = "link"

    def convert(self, args: List[str], context: Dict):
        return '<a href="{}">{}</a>'.format(*args)

class LiteralShortcode(PargShortcode):
    name = "link"

    def convert(self, args: List[str], context: Dict):
        return ", ".join(args)



def test_manager_basic_shortcode():
    sh = Shortcoder([BasicShortcode()])
    assert sh.parse("[%link one two %]") == '<a href="one">two</a>'

def test_manager_shortcode_format():
    shcode = LiteralShortcode()
    shcode.name = 'foo-bar'
    sh = Shortcoder([shcode])
    sh.parse("[%foo-bar one \"two two\" three 'four four' %]") == "one, two two, three, four four"
    sh.parse("[% foo-bar one \"two two\" three 'four four' %]") == "one, two two, three, four four"
    sh.parse("[% foo-bar one \"two two\" three 'four four'%]") == "one, two two, three, four four"


def test_manager_unknown_shortcode():
    sh = Shortcoder([BasicShortcode()])
    with pytest.raises(UnknownShortcode):
        assert sh.parse("[%linkz one two %]")

def test_manager_unknown_shortcode_key():
    class StrictKwargShortcode(KwargShortcode):
        name = "link"
        keys = ("src", "caption")
        
        def convert(self, kwargs: Dict[str, str], context: Optional[Dict] = None):
            return ", ".join(f"{k}={v}" for k, v in kwargs.items())

    # with key lock should raise on unknown keys
    sh = Shortcoder([StrictKwargShortcode()])
    assert sh.parse("[%link src=one.jpg caption=hi %]") == 'src=one.jpg, caption=hi'
    with pytest.raises(UnknownShortcodeKey):
        assert sh.parse("[%link src=one.jpg caption=hi extra=oops %]")

    # no key lock will be silent
    class NonStrictKwargShortcode(StrictKwargShortcode):
        keys = None
    sh = Shortcoder([NonStrictKwargShortcode()])
    assert sh.parse("[%link src=one.jpg caption=hi %]") == 'src=one.jpg, caption=hi'
    assert sh.parse("[%link src=one.jpg caption=hi extra=oops %]")






def test_manager_unpack():
    sh = Shortcoder([LiteralShortcode()])
    sh.parse("[%link one \"two two\" three 'four four' %]") == "one, two two, three, four four"


class LiteralKwargShortcode(KwargShortcode):
    name = "link"

    def convert(self, kwargs: Dict[str, str], context: Dict):
        return ", ".join(f"{k}={v}" for k, v in kwargs.items())


def test_manager_unpack_kwargs():
    sh = Shortcoder([LiteralKwargShortcode()])
    sh.parse("[%link key1=\"one two\" key2='three four' %]") == "key1=one two, key2=three four"

def test_manager_noshortcodes_registered():
    sh = Shortcoder()
    with pytest.raises(NoShortcodesRegistered):
        sh.parse("foobar")

def test_manager_duplicated_registered():
    with pytest.raises(DuplicateShortcode):
        Shortcoder([LiteralKwargShortcode, LiteralShortcode])