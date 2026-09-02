from model_setup import processor,model

def extract_visual_features(image):
    """Run the BLIP visual encoder to get pixel values and image feature embeddings."""
    inputs=processor(images=image,return_tensors="pt")
    pixel_values=inputs["pixel_values"]
    vision_outputs=model.vision_model(pixel_values=pixel_values)
    image_embeds=vision_outputs[0]
    return pixel_values,image_embeds

if __name__=="__main__":
    from image_preprocessing import preprocess_image

    image=preprocess_image("example.jpg")
    pixel_values,image_embeds=extract_visual_features(image)
    print("Pixel values shape:",pixel_values.shape)
    print("Visual feature embedding shape:",image_embeds.shape)
