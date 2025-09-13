import base64
from PIL import Image
from io import BytesIO

def img_base64(img_path):
    """Convert image to base64 string.

    Args:
        img_path (str): The path of the image.

    Returns:
        str: The base64 string of the image.
    """

    if not img_path:
        return None

    with open(img_path, "rb") as img_f:
        img_base64 = base64.b64encode(img_f.read()).decode("utf-8")
    return img_base64

def pil_image_base64(img_path):

    """Convert an image file to a base64 string using PIL for processing.

    Args:
        img_path (str): The path of the image file. If None, returns None.

    Returns:
        str or None: The base64 string of the image if img_path is valid, otherwise None.
    """

    if not img_path:
        return None

    with Image.open(img_path) as img:
        buffered = BytesIO()
        img.save(buffered, format=img.format)
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64
