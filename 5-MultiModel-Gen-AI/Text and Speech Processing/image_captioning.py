from multimodal_query import send_multimodal_query

def generate_image_caption(model,encoded_image):
    """Generate a descriptive caption for an image."""
    prompt="Please provide a detailed description of this image."
    return send_multimodal_query(model,encoded_image,prompt)

if __name__=="__main__":
    from multimodal_model_setup import model
    from image_processing import encode_image

    encoded_image=encode_image("example.jpg")
    caption=generate_image_caption(model,encoded_image)
    print("Image Caption:",caption)
