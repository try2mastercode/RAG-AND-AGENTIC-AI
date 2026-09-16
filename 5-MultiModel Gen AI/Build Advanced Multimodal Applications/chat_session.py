from model_setup import model

class ChatSession:
    """Keeps the running message history for a multi-turn multimodal chat."""

    def __init__(self):
        self.messages=[]

    def add_user_message(self,content):
        self.messages.append({"role":"user","content":content})

    def add_assistant_message(self,text):
        self.messages.append({"role":"assistant","content":text})

    def send(self):
        """Send the full conversation history to the model and record the reply."""
        response=model.chat(messages=self.messages)
        reply=response['choices'][0]['message']['content']
        self.add_assistant_message(reply)
        return reply

    def reset(self):
        self.messages=[]
