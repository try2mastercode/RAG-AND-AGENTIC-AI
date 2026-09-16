from PIL import Image

def preprocess_image(image_path):
    """Open a validated image file and convert it to RGB for model input."""
    return Image.open(image_path).convert('RGB')

if __name__=="__main__":
    image=preprocess_image("example.jpg")
    print("Preprocessed image size:",image.size)
