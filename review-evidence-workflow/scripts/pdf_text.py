"""Optional glyph-coordinate index for rendered pages (requires pdfplumber).
No OCR, fuzzy matching, or edits to the source PDF are performed.
"""
import hashlib
from pathlib import Path


def extract_pdf_words(path):
    import pdfplumber
    path = Path(path)
    pages = {}
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            words, previous, line_id = [], None, 0
            for word in page.extract_words(use_text_flow=True):
                if previous is None or abs(word['top'] - previous['top']) > 3 or word['x0'] < previous['x0'] or word['x0'] - previous['x1'] > 18:
                    line_id += 1
                words.append({'text': word['text'], 'line': line_id,
                              'x': round(word['x0'] / page.width, 6),
                              'y': round(word['top'] / page.height, 6),
                              'w': round((word['x1'] - word['x0']) / page.width, 6),
                              'h': round((word['bottom'] - word['top']) / page.height, 6)})
                previous = word
            pages[str(number)] = words
    return {'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'pages': pages}
