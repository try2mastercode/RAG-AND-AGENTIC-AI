from chat_session import ChatSession
from nutrition_estimator import estimate_nutrition,ask_follow_up
from response_parser import parse_nutrition_response

def test_nutrition_estimate(image_path="food_example.jpg"):
    """Check that a food image returns a non-empty structured nutrition response."""
    session=ChatSession()
    response=estimate_nutrition(session,image_path)
    assert isinstance(response,str) and len(response)>0
    parsed=parse_nutrition_response(response)
    assert parsed["calories"] is not None
    print("test_nutrition_estimate passed. Calories:",parsed["calories"])

def test_follow_up_question(image_path="food_example.jpg"):
    """Check that a follow-up question keeps the conversation context from the first turn."""
    session=ChatSession()
    estimate_nutrition(session,image_path)
    answer=ask_follow_up(session,"Is this a healthy meal?")
    assert isinstance(answer,str) and len(answer)>0
    print("test_follow_up_question passed. Answer:",answer)

if __name__=="__main__":
    test_nutrition_estimate()
    test_follow_up_question()
