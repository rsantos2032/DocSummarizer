import fitz
import numpy as np

# from .Parser import Parser

class PDFParser():
    # def extract_page_blocks(self):
    #     page_blocks = []
    #     for page in self.document:
    #         page.clean_contents()
    #         blocks = page.get_text('dict', flags=2)['blocks']
    #         page_blocks.append(blocks)
    #     return page_blocks
    
    # def extract_text_from_block(self, block):
    #     return ' '.join(' '.join(span['text'] for span in line['spans']) for line in block['lines'])
    
    def parse(self, path: str) -> str:
        self.document = fitz.open(path)
        text = ''
        for page in self.document:
            text = f"{text}{page.get_text()} "
        return text
