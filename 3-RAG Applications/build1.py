import gradio as gr
def process_number_and_text(text):
    return f"your enterd:'{text}'"
demo=gr.Interface(
    fn=process_number_and_text,

    inputs=[gr.Textbox(label="Enter some text "),
            gr.Number(label="Enter a number")
            ],
    outputs=gr.Textbox(label="output")

)
demo.launch()