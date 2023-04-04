from textwrap import dedent
import pytest
from shortcoder.manager import Shortcoder
from shortcoder.exceptions import InvalidInput, InvalidKeywords, ExtraParameters, RenderingError
from shortcoder.shortcodes.base import Input
from shortcoder.shortcodes.html import HtmlKwargShortcode, HtmlPargShortcode


url_kwarg_shortcode = HtmlKwargShortcode(
    "url",
    inputs=[
        Input("href", xpath="@href", required=True),
        Input("text", xpath="text()", default="foobar"),
    ],
    template="""<a rel="noopener noreferrer" target="_blank" href="{href}">{text}</a>""",
)
url2_kwarg_shortcode = HtmlKwargShortcode(
    "url2",
    inputs=[
        Input("href", xpath="@href"),
    ],
    template=lambda href: f'<a rel="noopener noreferrer" target="_blank" href="{href}">{href}</a>',
)


class TestKwargShortcodeConverting:
    def setup_method(self) -> None:
        self.sh = Shortcoder([url_kwarg_shortcode, url2_kwarg_shortcode])

    def test_order(self):
        """test kwarg order - it should not matter"""
        # check kwarg order
        assert (
            self.sh.parse("[%url href=foo.jpg text=image %]")
            == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg" class="shortcode-url">image</a>'
        )
        assert (
            self.sh.parse("[%url text=image href=foo.jpg %]")
            == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg" class="shortcode-url">image</a>'
        )

    def test_callable_template(self):
        """test when template is a callable function"""
        assert (
            self.sh.parse("[%url2 href=foo.jpg %]")
            == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg" class="shortcode-url2">foo.jpg</a>'
        )

    def test_defaults(self):
        """test whether input.default is being considered"""
        assert (
            self.sh.parse("[%url href=foo.jpg %]")
            == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg" class="shortcode-url">foobar</a>'
        )

    def test_required(self):
        """test when input.required is True and no value is provided"""
        with pytest.raises(RenderingError, match="Missing required input href for url shortcode"):
            self.sh.parse("[%url text=image %]")

    def test_unknown_key(self):
        """test when shortcode contains unknown key"""
        with pytest.raises(InvalidKeywords, match="""shortcode url got unknown keys """):
            self.sh.parse("[%url src=foo.jpg %]")


class TestKwargShortcodeReversing:
    def setup_method(self) -> None:
        self.sh = Shortcoder([url_kwarg_shortcode])

    def test_false_positives_when_missing_class(self):
        """check for false-positive reversals when HTML is encountered but doesn't contain shortcode class tag"""
        # check for false-positives
        assert (
            self.sh.reverse('<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image</a>')
            #                                                                          ^^ note no `class="shortcode-url"`
            == '<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image</a>'
        )

    def test_quotes_in_html(self):
        """check whether reversal can handle quote characters"""
        assert (
            self.sh.reverse(
                """<a href="foo's.jpg" rel="noopener noreferrer" target="_blank" class="shortcode-url">image</a>"""
                #             ^^^
            )
            == """[%url href="foo's.jpg" text=image %]"""
            #                   ^^^
        )

    def test_success(self):
        """check whether reversal works when everything is correct"""
        assert (
            self.sh.reverse(
                """<a href="foo.jpg" rel="noopener noreferrer" target="_blank" class="shortcode-url">image's</a>"""
            )
            == """[%url href=foo.jpg text="image's" %]"""
        )


url_pos_shortcode = HtmlPargShortcode(
    "url",
    inputs=[Input("href", xpath="@href"), Input("text", xpath="text()")],
    template="""<a rel="noopener noreferrer" target="_blank" href="{href}">{text}</a>""",
)


class TestPargConverting:
    def setup_method(self) -> None:
        self.sh = Shortcoder([url_pos_shortcode])
    

    def test_success(self):
        # 1 parameter
        assert (
            self.sh.parse("[%url foo.jpg image %]")
            == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg" class="shortcode-url">image</a>'
        )
        # all parameters
        assert (
            self.sh.parse("[%url foo.jpg %]")
            == '<a rel="noopener noreferrer" target="_blank" href="foo.jpg" class="shortcode-url"/>'
        )

    def test_extra_parameters(self):
        with pytest.raises(ExtraParameters, match="""shortcode url got 3 parameters when 2 expected"""):
            self.sh.parse("[%url foo.jpg bar gaz %]")

    def test_defaults_not_allowed(self):
        with pytest.raises(InvalidInput, match="Positional shortcodes do not support default values"):
            sh = Shortcoder([HtmlPargShortcode("url", inputs=[Input("href", xpath="@href", default="foobar")], template="")])



class TestPargReverse:
    def setup_method(self):
        self.sh = Shortcoder([url_pos_shortcode])

    def test_false_positive(self):
        assert (
            self.sh.reverse('<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image</a>')
            == '<a href="foo.jpg" rel="noopener noreferrer" target="_blank">image</a>'
        )

    def test_success(self):
        assert (
            self.sh.reverse(
                '<a href="foo.jpg" rel="noopener noreferrer" target="_blank" class="shortcode-url">image</a>'
            )
            == "[%url foo.jpg image %]"
        )
        assert (
            self.sh.reverse(
                """<a href="foo's.jpg" rel="noopener noreferrer" target="_blank" class="shortcode-url">image</a>"""
            )
            == """[%url "foo's.jpg" image %]"""
        )
        assert (
            self.sh.reverse(
                """<a href="foo.jpg" rel="noopener noreferrer" target="_blank" class="shortcode-url">image's</a>"""
            )
            == """[%url foo.jpg "image's" %]"""
        )
