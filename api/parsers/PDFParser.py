import fitz

from .Parser import Parser

class PDFParser():
    def parse(self, path: str) -> str:
        self.document = fitz.open(path)
        text = ''
        for page in self.document:
            text = f"{text}{page.get_text()} "
        return text
