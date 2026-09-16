from multimodal_query import send_multimodal_query

def visual_question_answering(model,encoded_image,question):
    """Answer questions about image content."""
    prompt=f"Please answer the following question about the image: {question}"
    return send_multimodal_query(model,encoded_image,prompt)

if __name__=="__main__":
    from multimodal_model_setup import model
    from image_processing import encode_image

    encoded_image=encode_image("example.jpg")
    question="What color is the cat in the image?"
    answer=visual_question_answering(model,encoded_image,question)
    print("Answer:",answer)
