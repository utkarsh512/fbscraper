"""
exceptions.py - Exceptions handling for fbscraper
"""

from selenium.common.exceptions import NoSuchElementException

class LoginError(Exception):
    """raised when facebook login is unsuccessful"""
    pass

class URLError(Exception):
    """raised when an invalid URL is given to scrape"""
    pass

class BadPostError(Exception):
    """raised when the post's metadata cannot be parsed"""
    pass

class SourceError(Exception):
    """raised when facebook page source has been updated"""
    pass
