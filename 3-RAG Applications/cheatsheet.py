import gradio as gr


# ==========================================
# 1. Define the Function (fn)
# ==========================================
def process_data(
        is_active,  # Maps to Checkbox (Boolean)
        hobbies,  # Maps to CheckboxGroup (List of strings)
        favorite_color,  # Maps to Dropdown (String)
        uploaded_file,  # Maps to File (File object/path)
        uploaded_image,  # Maps to Image (Numpy array/path)
        gender,  # Maps to Radio (String)
        age,  # Maps to Slider (Integer/Float)
        name  # Maps to Textbox (String)
):
    """
    This function wraps the Gradio inputs and returns a tuple for the outputs.
    The order of the parameters exactly matches the order of the 'inputs' list.
    """

    # Safely handle the file and image to avoid errors if the user skips them
    file_name = uploaded_file.name if uploaded_file is not None else "No file uploaded"
    image_status = "Image provided" if uploaded_image is not None else "No image provided"

    # First Output: Format a summary string for the Textbox
    summary = (
        f"Name: {name}\n"
        f"Age: {age}\n"
        f"Active: {is_active}\n"
        f"Hobbies: {', '.join(hobbies) if hobbies else 'None'}\n"
        f"Favorite Color: {favorite_color}\n"
        f"Gender: {gender}\n"
        f"File: {file_name}\n"
        f"Image: {image_status}"
    )

    # Second Output: Create a dictionary for the Label classification
    # Label components can accept a dict mapping classes to probabilities
    adult_prob = min(age / 100.0, 1.0)  # Calculates a mock probability based on age
    child_prob = 1.0 - adult_prob
    classification_dict = {"Adult": adult_prob, "Child": child_prob}

    # Return a tuple mapping to (Textbox output, Label output)
    return summary, classification_dict


# ==========================================
# 2. Define the Inputs
# ==========================================
# The number of inputs must match the number of arguments in the function above.
inputs_list = [
    gr.Checkbox(label="Is Active?"),  # checkbox
    gr.CheckboxGroup(["Reading", "Coding", "Sports"], label="Hobbies"),  # checkboxGroup
    gr.Dropdown(["Red", "Blue", "Green"], label="Favorite Color"),  # dropdown
    gr.File(label="Upload a File"),  # file
    gr.Image(label="Upload an Image"),  # image
    gr.Radio(["Male", "Female", "Other"], label="Gender"),  # radio
    gr.Slider(minimum=0, maximum=100, step=1, value=25, label="Age"),  # slider
    gr.Textbox(label="Enter your Name")  # textbox
]

# ==========================================
# 3. Define the Outputs
# ==========================================
outputs_list = [
    gr.Textbox(label="Summary Textbox"),  # textbox
    gr.Label(num_top_classes=2, label="Age Classification Predictor")  # label
]

# ==========================================
# 4. Create the Interface & Launch
# ==========================================
demo = gr.Interface(
    fn=process_data,
    inputs=inputs_list,
    outputs=outputs_list,
    title="Gradio Cheat Sheet App",
    description="A demonstration of all common Gradio inputs and outputs."
)

# Launching with share=True creates a public URL worldwide.
# The processing still runs on your local machine.
if __name__ == "__main__":
    demo.launch(share=True)