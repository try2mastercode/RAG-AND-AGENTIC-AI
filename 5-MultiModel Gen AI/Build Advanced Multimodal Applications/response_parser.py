import re

FIELD_PATTERNS={
    "food":r"Food identified:\s*(.+)",
    "serving_size":r"Estimated serving size:\s*(.+)",
    "calories":r"Calories:\s*(.+)",
    "protein":r"Protein:\s*(.+)",
    "carbohydrates":r"Carbohydrates:\s*(.+)",
    "fiber":r"Fiber:\s*(.+)",
    "fat":r"Fat:\s*(.+)",
    "vitamins_minerals":r"Key vitamins and minerals:\s*(.+)"
}

def parse_nutrition_response(response_text):
    """Pull each nutrition field out of the model's structured reply into a dict."""
    result={}
    for field,pattern in FIELD_PATTERNS.items():
        match=re.search(pattern,response_text)
        result[field]=match.group(1).strip() if match else None
    return result

if __name__=="__main__":
    sample_response="""Food identified: Grilled chicken breast with steamed broccoli
Estimated serving size: 200g chicken, 100g broccoli
Calories: 330 kcal
Protein: 45g
Carbohydrates: 8g
Fiber: 3g
Fat: 9g
Key vitamins and minerals: Vitamin C, Vitamin K, Iron, Potassium"""

    parsed=parse_nutrition_response(sample_response)
    for field,value in parsed.items():
        print(f"{field}: {value}")
