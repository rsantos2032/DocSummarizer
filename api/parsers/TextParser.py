from .Parser import Parser

# class TextParser(Parser):
class TextParser:
    def parse(self, file):
        text = ''
        with open(file) as fp:
            text = fp.read()
        return text