import base64
import io
import PIL as Image

def b64_to_pil(content):
    decoded = base64.b64decode(content)
    buffer = io.BytesIO(decoded)
    img = Image.open(buffer)
    return img
