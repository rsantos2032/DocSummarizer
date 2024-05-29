from .Parser import Parser

import docx

class DocxParser(Parser):
    def parse(self, path: str) -> str:
        doc = docx.Document(path)
        text = []
        for p in doc.paragraphs:
            text.append(p.text)
        return ' '.join(text)