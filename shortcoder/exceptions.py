class UnknownShortcode(BaseException):
    """raised when unregistered shortcode is encountered"""


class ExtraParameters(BaseException):
    """raised when shortcode is passed too many positional parameters"""


class InvalidKeywords(BaseException):
    """raised when shortcode is passed invalid keywords"""


class DuplicateShortcode(BaseException):
    """raised when multiple shortcodes share the same shortcode name"""


class NoShortcodesRegistered(BaseException):
    """raised when shortcode manager has no shortcodes registered and is requested to parse text"""


class ShotcodeNotReversible(BaseException):
    """raised when shortcode has no reversibility implemented and is being reversed by the manager"""
