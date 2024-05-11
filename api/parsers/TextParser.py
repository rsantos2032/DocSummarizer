from Parser import Parser

class TextParser(Parser):
    def parse(self, file):
        text = ''
        with open(file) as fp:
            text = fp.read()
        return text

parser = TextParser()
print(parser.parse('test.txt'))