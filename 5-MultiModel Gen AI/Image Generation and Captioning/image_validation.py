from PIL import Image,UnidentifiedImageError

def is_valid_image(image_path):
    """Return True if the file exists and can be opened as an image."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except (FileNotFoundError,UnidentifiedImageError,OSError):
        return False

if __name__=="__main__":
    print("example.jpg valid:",is_valid_image("example.jpg"))
    print("not_a_real_file.jpg valid:",is_valid_image("not_a_real_file.jpg"))
