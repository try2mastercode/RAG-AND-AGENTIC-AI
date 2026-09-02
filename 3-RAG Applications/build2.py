import gradio as gr


def count_files(files):
    return f"jNumber of files uploaded :{len(files)}"


demo = gr.Interface(
    fn=count_files,
    inputs = gr.File(file_count="multiple",
                        type="filepath",
                        label="Upload or drag the file here"
                        ),
    outputs = gr.Textbox(label="Number of files uploaded")
)
demo.launch()