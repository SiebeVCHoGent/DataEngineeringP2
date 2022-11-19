import fitz
from io import BytesIO
from PIL import Image
from pytesseract import *

pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'


def read_pdf(content_stream):
    '''
    reads pdf content and returns text
    '''
    pdf_file = fitz.open(stream=content_stream, filetype="pdf")
    text = ''

    for page in pdf_file:

        # Handle Text
        text += page.get_text()

        # Handle Images
        for _, img in enumerate(page.get_images(), start=1):
            # get the XREF of the image
            xref = img[0]

            # Get bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image['image']

            with Image.open(BytesIO(image_bytes)) as image:
                # Read Image with OCR
                try:
                    image_text = image_to_string(image)
                    text += f'\n{image_text}'
                except TypeError as type_error:
                    print(f'Error in extract_data\n{type_error}')
    return str(text)