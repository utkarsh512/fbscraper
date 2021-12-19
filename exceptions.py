class LoginError(Exception):
    """raised when facebook login is unsuccessful"""
    pass

class URLError(Exception):
    """raised when an invalid URL is given to scrape"""
    pass

class BadPostError(Exception):
    """raised when the post's metadata cannot be parsed"""
    pass
