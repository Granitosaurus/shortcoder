# Shortcoder

Bi-directional parser for wordpress style shortcodes. 

This tool is intended to be used with static site generators by providing a convenient way to insert complex HTML via short templates.

For example we can create shortcodes like:

```
# key value based shortcodes
[%url href=one.jpg text="my link" %]

# or positional arg shortcodes:
[%url one.jpg "my link" %]
```

that would be converted to:
```
<a src="https://mydomain.com/one.jpg" rel="noreferrer noopener">my link</a>
```
