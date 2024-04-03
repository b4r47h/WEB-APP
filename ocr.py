import easyocr
reader = easyocr.Reader(['en'])
def perform_ocr(image_path):
    reader = easyocr.Reader(['en'])
    output = reader.readtext(image_path)
    plate_text = ' '.join([item[1] for item in output])
    return plate_text


""" import easyocr
import numpy as np
from PIL import Image

def perform_ocr(image):
    reader = easyocr.Reader(['en'])
    if isinstance(image, str):
        result = reader.readtext(image)
    elif isinstance(image, np.ndarray):
        image_pil = Image.fromarray(image)
        result = reader.readtext(np.array(image_pil))
    else:
        raise ValueError('Invalid input type. Supporting format = string(file path or url), bytes, numpy array')
    
    return result
 """