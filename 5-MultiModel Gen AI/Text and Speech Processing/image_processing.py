import base64
from PIL import Image

def encode_image(image_path):
    """Convert image to base64 for model input."""
    with open(image_path,"rb") as image_file:
        encoded_string=base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def process_image(image_path,target_size=(224,224)):
    """Process image for model input."""
    image=Image.open(image_path)
    image=image.resize(target_size)
    return image

if __name__=="__main__":
    image_path="example.jpg"
    encoded_image=encode_image(image_path)
    processed_image=process_image(image_path)
