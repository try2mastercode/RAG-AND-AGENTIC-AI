def send_multimodal_query(model,encoded_image,prompt):
    """Send combined text and image query to model."""
    messages=[{
        "role":"user",
        "content":[
            {
                "type":"text",
                "text":prompt
            },
            {
                "type":"image_url",
                "image_url":{
                    "url":f"data:image/jpeg;base64,{encoded_image}"
                }
            }
        ]
    }]
    response=model.chat(messages=messages)
    return response['choices'][0]['message']['content']

if __name__=="__main__":
    from multimodal_model_setup import model
    from image_processing import encode_image

    encoded_image=encode_image("example.jpg")
    prompt="Please provide a detailed description of this image."
    response=send_multimodal_query(model,encoded_image,prompt)
    print("Model Response:",response)
