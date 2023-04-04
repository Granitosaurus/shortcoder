"""
This example illustrates a youtube video shortcode for embedding youtube videos:
    [%yt 2fmCcfAb4k4 %]
    🔃
    <iframe width="560" height="315" data-id="2fmCcfAb4k4" src="https://www.youtube.com/embed/2fmCcfAb4k4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen class="shortcode-yt"></iframe>
"""
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