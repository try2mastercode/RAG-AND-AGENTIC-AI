from image_validation import is_valid_image
from image_preprocessing import preprocess_image
from image_encoding import encode_image_base64
from visual_feature_extractor import extract_visual_features
from multimodal_fusion import fuse_and_generate_caption

def generate_image_caption(image_path,text_prompt=None):
    """Run the full pipeline: validate, preprocess, encode, extract features, fuse, and caption."""
    if not is_valid_image(image_path):
        return "The image is not valid."

    image=preprocess_image(image_path)
    encoded_image=encode_image_base64(image_path)
    pixel_values,image_embeds=extract_visual_features(image)
    caption=fuse_and_generate_caption(pixel_values,text_prompt)
    return caption

if __name__=="__main__":
    print("Valid image result:",generate_image_caption("example.jpg"))
    print("Invalid image result:",generate_image_caption("not_a_real_file.jpg"))
