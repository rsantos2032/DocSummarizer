from .Parser import Parser


# class TextParser(Parser):
class TextParser(Parser):
    def parse(self, path: str) -> str:
        text = ''
        with open(path) as fp:
            text = fp.read()
        return text