import gradio as gr
from caption_pipeline import generate_image_caption

def caption_image(image_path):
    """Gradio callback: run the full captioning pipeline on the uploaded image."""
    return generate_image_caption(image_path)

demo=gr.Interface(
    fn=caption_image,
    inputs=gr.Image(type="filepath"),
    outputs=gr.Textbox(label="Generated Caption"),
    title="Image Captioning App",
    description="Upload an image and get an AI-generated caption using BLIP."
)

if __name__=="__main__":
    demo.launch()
