class UnknownShortcode(BaseException):
    """raised when unregistered shortcode is encountered"""
    pass


class UnknownShortcodeKey(BaseException):
    """raised when kwargshortcode encounters unknown key"""
    pass


class DuplicateShortcode(BaseException):
    """raised when multiple shortcodes share the same shortcode name"""
    pass


class NoShortcodesRegistered(BaseException):
    """raised when shortcode manager has no shortcodes registered and is requested to parse text"""
    pass


class ShotcodeNotReversible(BaseException):
    """raised when shortcode has no reversibility implemented and is being reversed by the manager"""
    pass
