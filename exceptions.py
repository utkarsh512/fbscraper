class LoginError(Exception):
    """raised when facebook login is unsuccessful"""
    pass

class URLError(Exception):
    """raised when an invalid URL is given to scrape"""
    pass
