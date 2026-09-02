from image_preprocessing import preprocess_image
from visual_feature_extractor import extract_visual_features
from multimodal_fusion import fuse_and_generate_caption
from caption_pipeline import generate_image_caption

def test_embedding_extraction(image_path="example.jpg"):
    """Check that the visual encoder produces a non-empty feature embedding."""
    image=preprocess_image(image_path)
    pixel_values,image_embeds=extract_visual_features(image)
    assert image_embeds.shape[-1]>0
    print("test_embedding_extraction passed. Embedding shape:",image_embeds.shape)

def test_caption_query(image_path="example.jpg",text_prompt="a photograph of"):
    """Check that a captioning query returns a non-empty caption string."""
    image=preprocess_image(image_path)
    pixel_values,_=extract_visual_features(image)
    caption=fuse_and_generate_caption(pixel_values,text_prompt)
    assert isinstance(caption,str) and len(caption)>0
    print("test_caption_query passed. Caption:",caption)

def test_invalid_image(image_path="not_a_real_file.jpg"):
    """Check that an invalid image path is rejected before reaching the model."""
    result=generate_image_caption(image_path)
    assert result=="The image is not valid."
    print("test_invalid_image passed.")

if __name__=="__main__":
    test_embedding_extraction()
    test_caption_query()
    test_invalid_image()
