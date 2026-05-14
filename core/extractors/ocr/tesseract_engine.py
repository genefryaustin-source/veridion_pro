import io

import pytesseract

from PIL import Image
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def run_ocr(
    image_bytes: bytes,
) -> str:

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        text = pytesseract.image_to_string(
            image
        )

        return text or ""

    except Exception as e:

        print(
            "❌ OCR FAILED:",
            e
        )

        return ""