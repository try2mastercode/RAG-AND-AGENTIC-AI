import base64

def encode_image(image_path):
    """Convert an image file to a base64 string for a multimodal chat message."""
    with open(image_path,"rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

if __name__=="__main__":
    encoded=encode_image("food_example.jpg")
    print("Base64 length:",len(encoded))
