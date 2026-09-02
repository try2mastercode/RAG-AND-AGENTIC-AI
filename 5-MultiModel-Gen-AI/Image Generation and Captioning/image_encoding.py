import base64
from io import BytesIO
from PIL import Image

def encode_image_base64(image_path):
    """Convert an image file to a base64-encoded string."""
    with open(image_path,"rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def decode_base64_image(encoded_string):
    """Convert a base64-encoded string back into a PIL image."""
    image_bytes=base64.b64decode(encoded_string)
    return Image.open(BytesIO(image_bytes)).convert('RGB')

if __name__=="__main__":
    encoded_image=encode_image_base64("example.jpg")
    print("Base64 length:",len(encoded_image))
    decoded_image=decode_base64_image(encoded_image)
    print("Decoded image size:",decoded_image.size)
