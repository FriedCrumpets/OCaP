#! Python3

class Error(Exception):
    """Base class for exceptions in this module"""
    pass

class IncorrectFile(Error):
    """Raised if the file is not recognised"""
    def __init__(self, message):
        self.message = message

class PriceNotNumber(Error):
    """Raised if the value parsed is not an integer"""
    def __init__(self, message):
        self.message = message

class convert(Error):
    """Raised if file not recongnised"""
    def __init__(self, file, *args):
        self.message = f'{file} not recognised'
