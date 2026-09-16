from model_setup import processor,model

def fuse_and_generate_caption(pixel_values,text_prompt=None):
    """Fuse visual features with the text decoder via cross-attention and generate a caption."""
    if text_prompt:
        text_inputs=processor(text=text_prompt,return_tensors="pt")
        output=model.generate(pixel_values=pixel_values,input_ids=text_inputs["input_ids"],max_new_tokens=50)
    else:
        output=model.generate(pixel_values=pixel_values,max_new_tokens=50)
    caption=processor.decode(output[0],skip_special_tokens=True)
    return caption

if __name__=="__main__":
    from image_preprocessing import preprocess_image
    from visual_feature_extractor import extract_visual_features

    image=preprocess_image("example.jpg")
    pixel_values,_=extract_visual_features(image)
    caption=fuse_and_generate_caption(pixel_values)
    print("Generated Caption:",caption)
