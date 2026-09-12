import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_text_from_image(image_path: str) -> str:
    """Ek image file se text nikalta hai"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF ko pehle images mein convert karta hai, fir har page se text nikalta hai"""
    pages = convert_from_path(pdf_path)
    full_text = ""
    for i, page in enumerate(pages):
        full_text += f"\n--- Page {i+1} ---\n"
        full_text += pytesseract.image_to_string(page)
    return full_text

def extract_text(file_path: str) -> str:
    """File type dekh kar sahi function call karta hai"""
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    else:
        return extract_text_from_image(file_path)