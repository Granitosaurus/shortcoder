import pytest
from shortcoder import PositionalShortcode, Input
from shortcoder.exceptions import InvalidInput

class TestPargInit:
    def test_defaults(self):
        with pytest.raises(InvalidInput, match="foo has default abc but is not trailing"):
            PositionalShortcode("test", inputs=[Input("foo", default="abc"), Input("bar")])
        with pytest.raises(InvalidInput, match="bar has default abc but is not trailing"):
            PositionalShortcode("test", inputs=[Input("foo"), Input("bar", default="abc"), Input("gaz")])
        PositionalShortcode("test", inputs=[Input("foo", default="abc"), Input("bar", default="abc")])