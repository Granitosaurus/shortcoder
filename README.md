# Shortcoder

Bi-directional parser for wordpress-style shortcodes:
```
[%link http://example.com "my link" %]
🔃
<a href="http://example.com">my link</a>
```

This tool is intended to be used with static site generators by providing a convenient way to insert complex HTML via short templates.

For example, embedding Youtube videos in markdown can take a lot of space:

```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/2fmCcfAb4k4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen data-id="2fmCcfAb4k4"></iframe>
```

Using Shortcoder this can be turned into a shortcode `[%yt 2fmCcfAb4k4 %]` which can be easily reversed back to the original HTML:

```python
from shortcoder import Shortcoder, HtmlPargShortcode, Input

# define a shortcode that will embed a youtube video
yt_embed = HtmlPargShortcode(
    "yt",
    inputs=[Input("id", xpath="@data-id")], 
    template="""<iframe width="560" height="315" data-id="{id}" src="https://www.youtube.com/embed/{id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>"""
)

# use shortcoder to parse shortcodes in text:
sh = Shortcoder([yt_embed])
result = sh.parse('Check out my youtube video\n[%yt 2fmCcfAb4k4 %]')
print(result)
"""
Check out my youtube video
<iframe width="560" height="315" data-id="2fmCcfAb4k4" src="https://www.youtube.com/embed/2fmCcfAb4k4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen class="shortcode-yt"></iframe>
"""
print(sh.reverse(result))
"""
Check out my youtube video
[%yt 2fmCcfAb4k4 %]
"""
```

For more, see the [examples](/examples) directory.

## Credits and Similar Packages

Shortcoder is inspired by [shortcodes](https://github.com/dmulholl/shortcodes) package with few key differences:

- bi-directionality supports. Shortcoder allows shorcodes to be reversed.
- focus on OOP programming for easier testing and extension.