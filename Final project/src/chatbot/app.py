import json
import logging

import gradio as gr

from agents.graph import build_graph
from chatbot.preferences import classify_intent, extract_preferences
from data.cli import add_restaurant, delete_restaurant, edit_restaurant, load_restaurants, save_restaurants

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_compiled_graph = None

CLARIFICATION_REPLY = (
    "I'd be happy to help! Are you looking for restaurant recommendations, recipe "
    "ideas, or both? Tell me a bit about your preferences (cuisines, dietary "
    "restrictions, budget) and I'll take it from there."
)

SAMPLE_PROMPTS = [
    "I'm vegetarian and love spicy Thai food, any restaurant ideas?",
    "I want to try cooking Vietnamese food at home, got a recipe?",
    "Budget-friendly comfort food for a casual weeknight dinner",
]


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def respond(message: str) -> str:
    intent = classify_intent(message)
    logger.info("intent=%s message=%r", intent, message)

    if intent == "clarification":
        return CLARIFICATION_REPLY

    preferences = extract_preferences(message)
    logger.info("preferences=%s", preferences)

    initial_state = {
        "user_id": "chat_session",
        "visit_history": [],
        "social_posts": [message, json.dumps(preferences)],
        "errors": [],
    }

    try:
        result = _get_graph().invoke(initial_state)
    except Exception as e:
        logger.error("workflow failed: %s", e)
        return f"Sorry, something went wrong while putting together recommendations: {e}"

    return result.get("final_recommendations") or "Sorry, I couldn't come up with a recommendation this time."


def _user_turn(message: str, history: list[dict]) -> tuple[str, list[dict]]:
    history = history + [{"role": "user", "content": message}]
    return "", history


def _bot_turn(history: list[dict]) -> list[dict]:
    last_user_message = history[-1]["content"]
    reply = respond(last_user_message)
    return history + [{"role": "assistant", "content": reply}]


def _restaurant_summary_text() -> str:
    records = load_restaurants()
    if not records:
        return "(no restaurants yet)"
    return "\n".join(f"{r['id']}: {r['name']} ({r['cuisine']}, {r['location']})" for r in records)


def _add_restaurant_ui(raw_text: str) -> str:
    if not raw_text.strip():
        return "Please paste a restaurant description first."
    try:
        records = load_restaurants()
        updated = add_restaurant(records, raw_text)
        save_restaurants(updated)
        return f"Added: {updated[-1]['name']} (id={updated[-1]['id']})\n\n{_restaurant_summary_text()}"
    except Exception as e:
        return f"Could not add restaurant: {e}"


def _delete_restaurant_ui(restaurant_id: str) -> str:
    if not restaurant_id.strip():
        return "Please enter a restaurant id first."
    try:
        records = load_restaurants()
        updated = delete_restaurant(records, restaurant_id.strip())
        save_restaurants(updated)
        return f"Deleted {restaurant_id}.\n\n{_restaurant_summary_text()}"
    except Exception as e:
        return f"Could not delete restaurant: {e}"


def _update_rating_ui(restaurant_id: str, new_rating: float) -> str:
    if not restaurant_id.strip():
        return "Please enter a restaurant id first."
    try:
        records = load_restaurants()
        updated = edit_restaurant(records, restaurant_id.strip(), {"rating": float(new_rating)})
        save_restaurants(updated)
        return f"Updated {restaurant_id} rating to {new_rating}.\n\n{_restaurant_summary_text()}"
    except Exception as e:
        return f"Could not update restaurant: {e}"


def build_app() -> gr.Blocks:
    with gr.Blocks(title="California Restaurant & Recipe Recommender") as demo:
        gr.Markdown("# California Restaurant & Recipe Recommender")

        with gr.Tab("Chat"):
            # latex_delimiters=[]: recommendations naturally contain $/$$/$$$ price
            # symbols, and Gradio's default LaTeX delimiters treat "$...$" as math
            # mode - an odd number of dollar signs anywhere in a response swallows
            # everything up to the next one into mangled, space-stripped math-italic
            # text. Confirmed live: a table cell with "$)" broke rendering for the
            # rest of the message.
            chatbot = gr.Chatbot(label="Recommender", latex_delimiters=[])
            msg = gr.Textbox(placeholder="Tell me what you're craving...", label="Your message")

            with gr.Row():
                for prompt in SAMPLE_PROMPTS:
                    gr.Button(prompt, size="sm").click(
                        lambda p=prompt: p, outputs=msg
                    )

            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")

            msg.submit(_user_turn, [msg, chatbot], [msg, chatbot]).then(_bot_turn, chatbot, chatbot)
            submit_btn.click(_user_turn, [msg, chatbot], [msg, chatbot]).then(_bot_turn, chatbot, chatbot)
            clear_btn.click(lambda: [], None, chatbot)

        with gr.Tab("Manage Restaurants"):
            gr.Markdown("Add, update, or delete restaurant records in the knowledge base.")
            summary_box = gr.Textbox(label="Current restaurants", value=_restaurant_summary_text, lines=10)

            with gr.Accordion("Add restaurant", open=False):
                new_desc = gr.Textbox(label="Raw restaurant description", lines=3)
                add_btn = gr.Button("Add")
                add_btn.click(_add_restaurant_ui, new_desc, summary_box)

            with gr.Accordion("Update rating", open=False):
                update_id = gr.Textbox(label="Restaurant id")
                update_rating = gr.Number(label="New rating", minimum=0, maximum=5)
                update_btn = gr.Button("Update")
                update_btn.click(_update_rating_ui, [update_id, update_rating], summary_box)

            with gr.Accordion("Delete restaurant", open=False):
                delete_id = gr.Textbox(label="Restaurant id")
                delete_btn = gr.Button("Delete")
                delete_btn.click(_delete_restaurant_ui, delete_id, summary_box)

    return demo


if __name__ == "__main__":
    build_app().launch()
