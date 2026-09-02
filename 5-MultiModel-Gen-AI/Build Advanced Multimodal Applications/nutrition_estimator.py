from image_encoding import encode_image
from nutrition_prompt import build_nutrition_message

def estimate_nutrition(chat_session,image_path):
    """Send a food image to the chatbot and get back an estimated nutrition breakdown."""
    encoded_image=encode_image(image_path)
    content=build_nutrition_message(encoded_image)
    chat_session.add_user_message(content)
    return chat_session.send()

def ask_follow_up(chat_session,question):
    """Ask a follow-up question about the food already shared earlier in this session."""
    chat_session.add_user_message(question)
    return chat_session.send()

if __name__=="__main__":
    from chat_session import ChatSession

    session=ChatSession()
    answer=estimate_nutrition(session,"food_example.jpg")
    print("Nutrition Estimate:\n",answer)

    follow_up=ask_follow_up(session,"What if I only eat half of this portion?")
    print("\nFollow-up Answer:\n",follow_up)
