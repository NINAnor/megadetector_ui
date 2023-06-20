import base64
import io
from PIL import Image

def b64_to_pil(content):
    decoded = base64.b64decode(content)
    buffer = io.BytesIO(decoded)
    img = Image.open(buffer)
    return img
