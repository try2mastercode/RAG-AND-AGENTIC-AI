def create_prompt(image_description,user_query):
    """Create a structured prompt for multimodal analysis."""
    prompt=f"""
    Analyze the following image and answer the question.
    Image Description: {image_description}
    User Query: {user_query}
    Please provide a detailed response that:
    1. Describes the image content
    2. Answers the specific question
    3. Provides relevant context
    """
    return prompt

if __name__=="__main__":
    image_desc="A cat sitting on a windowsill"
    user_question="What is the cat doing?"
    prompt=create_prompt(image_desc,user_question)
    print(prompt)
