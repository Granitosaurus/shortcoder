"""
This example illustrates simple <a></a> link shortcodes.

The first one is using positional arguments:
    [%link http://example.com/ text %]
    🔃
    <a href="http://example.com/">text</a>

the second one is using keyword arguments.
    [%link href=http://example.com/ text=text %]
    🔃
    <a href="http://example.com/">text</a>
"""
from shortcoder import Shortcoder, HtmlPargShortcode, Input, HtmlKwargShortcode

#        Positional Shortcode
# -----------------------------------------------

html_link = HtmlPargShortcode(
    "link",
    # [%link http://example.com/ text %]
    inputs=[
        Input("url", xpath="@href"),
        Input("text", xpath="text()"),
    ],
    # <a href="http://example.com/">text</a>%]
    template='<a href="{url}" class="blue">{text}</a>',
)

sh = Shortcoder([html_link])

# convert shortcodes to html
print(sh.parse("Follow me on [%link https://mastodon.technology/@Wraptile mastodon! %]"))
'Follow me on <a href="https://mastodon.technology/@Wraptile" class="blue shortcode-link">mastodon!</a>'

# reverse html to shortcodes:
print(sh.reverse('Follow me on <a href="https://mastodon.technology/@Wraptile" class="blue shortcode-link">mastodon!</a>'))
"Follow me on [%link https://mastodon.technology/@Wraptile mastodon! %]"

#        Keyword Shortcode
# -----------------------------------------------

html_link = HtmlKwargShortcode(
    "link",
    # [%link url=http://example.com/ text="some text" %]
    inputs=[
        Input("url", xpath="@href"),
        Input("text", xpath="text()", default="some link"),
    ],
    # <a href="http://example.com/">some text</a>%]
    template='<a href="{url}" class="blue">{text}</a>',
)

sh = Shortcoder([html_link])

print(sh.parse("""Follow me on [%link url=https://mastodon.technology/@Wraptile text="mastodon!" %]"""))
'Follow me on <a href="https://mastodon.technology/@Wraptile" class="blue shortcode-link">mastodon!</a>'
print(sh.reverse('Follow me on <a href="https://mastodon.technology/@Wraptile" class="blue shortcode-link">mastodon!</a>'))
"Follow me on [%link url=https://mastodon.technology/@Wraptile text=mastodon! %]"