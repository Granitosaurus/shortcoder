from typing import Union, Dict, List


def quote(text):
    """quote text if it contains any quotes in it"""
    if '"' in text:
        return f"'{text}'"
    if "'" in text:
        return f'"{text}"'
    if " " in text:
        return f'"{text}"'
    return text


def quote_values(values: Union[Dict[str, str], List[str]]):
    """
    quote kwarg or arg values if they need to be quoted, i.e. contain a space in them
    foo bar -> "foo bar"
    foo -> "foo"
    """
    if isinstance(values, Dict):
        return {k: quote(v) if v else v for k, v in values.items()}
    else:
        return [quote(v) if v else v for v in values]
