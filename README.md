# Shortcoder

Bi-directional parser for wordpress-style shortcodes. 

This tool is intended to be used with static site generators by providing a convenient way to insert complex HTML via short templates.

For example we can create shortcodes like:

```markdown
We can use key value based shortcodes:
[%url href=one.jpg text="my link" %]

or positional arg shortcodes:
[%url one.jpg "my link" %]
```

that would be converted to:
```
We can use key value based shortcodes:
<a src="https://mydomain.com/one.jpg" rel="noreferrer noopener">my link</a>

or positional arg shortcodes:
<a src="https://mydomain.com/one.jpg" rel="noreferrer noopener">my link</a>
```

## Example Usage

```python
from typing import List, Dict
from shortcoder import PositionalShortcode, Shortcoder


class LinkShortcode(PositionalShortcode):

    def convert(self, args: List[str], context: Dict):
        return '<a href="{}">{}</a>'.format(*args)
    
    def reverse(self, text):
        return self._rejoin()


shortcoder = Shortcoder([LinkShortcode()])
input = """Follow me on [%link https://mastodon.technology/@Wraptile mastodon! %]"""
print(shortcoder.parse(input))
# will print:
# Follow me on <mastodon! href="https://mastodon.technology/@Wraptile">mastodon!</a>
```

See example shortcodes over at [/examples](./examples/link.py)

## Credits and Similar Packages

Shortcoder is inspired by [shortcodes](https://github.com/dmulholl/shortcodes) package with few key differences:

- bi-directionality supports. Shortcoder allows shorcodes to be reversed.
- focus on OOP programming for easier testing and extension.