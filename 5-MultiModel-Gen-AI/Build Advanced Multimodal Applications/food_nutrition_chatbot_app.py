import gradio as gr
from chat_session import ChatSession
from nutrition_estimator import estimate_nutrition,ask_follow_up

session=ChatSession()

def chat_with_nutrition_bot(message,history):
    """Gradio callback: an attached image gets a nutrition estimate, plain text is a follow-up question."""
    text=message.get("text","")
    files=message.get("files",[])

    if files:
        return estimate_nutrition(session,files[0])
    return ask_follow_up(session,text)

demo=gr.ChatInterface(
    fn=chat_with_nutrition_bot,
    multimodal=True,
    title="Food Nutrition Chatbot",
    description="Upload a photo of your food to get an estimated calorie, protein, fiber and nutrient breakdown. Ask follow-up questions after."
)

if __name__=="__main__":
    demo.launch()
