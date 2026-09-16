NUTRITION_PROMPT="""You are a nutrition analysis assistant. Look at the food in this image and estimate its nutritional content.

Respond in this exact format:
Food identified: <name(s) of the food item(s)>
Estimated serving size: <approximate portion size>
Calories: <kcal>
Protein: <grams>
Carbohydrates: <grams>
Fiber: <grams>
Fat: <grams>
Key vitamins and minerals: <comma-separated list>

These are rough estimates based on a typical serving, not a lab measurement."""

def build_nutrition_message(encoded_image):
    """Build a multimodal chat message: the food image plus the nutrition prompt."""
    return [
        {
            "type":"text",
            "text":NUTRITION_PROMPT
        },
        {
            "type":"image_url",
            "image_url":{
                "url":f"data:image/jpeg;base64,{encoded_image}"
            }
        }
    ]
