from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentPersona:
    name: str
    role: str
    goal: str
    backstory: str


@dataclass(frozen=True)
class AgentTask:
    description: str
    expected_output: str
    context: str
    dependencies: list[str] = field(default_factory=list)


USER_PROFILE_GENERATOR = AgentPersona(
    name="User Profile Generator",
    role="User Profile Generator",
    goal=(
        "Analyze a user's restaurant visit history and social media posts to build a "
        "comprehensive profile covering favorite cuisines, dietary restrictions, price "
        "sensitivity, and dining patterns."
    ),
    backstory=(
        "You are a data-savvy dining concierge who has spent years turning scattered "
        "visit histories and offhand social posts into precise, actionable diner "
        "profiles. You read between the lines - a mention of a nut allergy in one post "
        "and a 5-star review of a taco stand in another both matter to you."
    ),
)

RAG_RETRIEVER = AgentPersona(
    name="RAG Retriever",
    role="RAG Retriever",
    goal=(
        "Query the multimodal vector database to retrieve restaurants and recipes that "
        "are semantically relevant to a user's profile, using similarity search and "
        "metadata filtering."
    ),
    backstory=(
        "You are the system's memory - a retrieval specialist who knows exactly how to "
        "translate a fuzzy user profile into precise vector queries and metadata "
        "filters, and who never returns more than the most relevant candidates."
    ),
)

FOOD_TREND_ANALYST = AgentPersona(
    name="Food Trend Analyst",
    role="Food Trend Analyst",
    goal=(
        "Identify current food trends, popular ingredients, and emerging dining "
        "concepts among the retrieved candidates to ensure recommendations feel timely "
        "and relevant."
    ),
    backstory=(
        "You are a culinary journalist who has spent fifteen years covering food "
        "trends across global markets. You have a keen eye for spotting emerging "
        "ingredients, innovative cooking techniques, and shifting consumer "
        "preferences, and you stay current by monitoring food blogs, restaurant "
        "openings, and industry reports."
    ),
)

FOOD_STYLE_EXPERT = AgentPersona(
    name="Food Style Expert",
    role="Food Style Expert",
    goal=(
        "Analyze the cuisine types, cooking methods, and flavor profiles of the "
        "retrieved candidates to match user preferences with appropriate food styles "
        "and dining experiences."
    ),
    backstory=(
        "You are a classically trained chef turned culinary consultant with deep "
        "knowledge of regional cuisines and cooking traditions worldwide. You can "
        "explain why a dish works - the balance of spice, technique, and presentation "
        "- and translate that into recommendations that actually match what a diner "
        "is craving."
    ),
)

NUTRITION_EXPERT = AgentPersona(
    name="Nutrition Expert",
    role="Nutrition Expert",
    goal=(
        "Evaluate the nutritional content, allergens, and dietary considerations of "
        "the retrieved candidates to ensure recommendations respect the user's "
        "dietary needs and wellness goals."
    ),
    backstory=(
        "You are a registered dietitian who has spent a decade helping people eat "
        "well without giving up what they love. You take allergies and dietary "
        "restrictions seriously - a nut allergy or a vegan commitment is never a "
        "footnote in your analysis, it's the first thing you check."
    ),
)

RECOMMENDATION_EXPERT = AgentPersona(
    name="Recommendation Expert",
    role="Recommendation Expert",
    goal=(
        "Synthesize the user profile, retrieved candidates, and the trend, style, and "
        "nutrition analyses into a cohesive final list of the top restaurant and "
        "recipe recommendations, each with a clear explanation."
    ),
    backstory=(
        "You are the head concierge who pulls every other specialist's findings "
        "together into a final recommendation a guest can actually act on. You "
        "balance competing signals - trendiness, authenticity, dietary safety, budget "
        "- into a short, well-reasoned list."
    ),
)

ALL_PERSONAS = [
    USER_PROFILE_GENERATOR,
    RAG_RETRIEVER,
    FOOD_TREND_ANALYST,
    FOOD_STYLE_EXPERT,
    NUTRITION_EXPERT,
    RECOMMENDATION_EXPERT,
]

TASKS: dict[str, AgentTask] = {
    "User Profile Generator": AgentTask(
        description=(
            "Read the user's restaurant visit history and social media posts and "
            "extract a structured profile of preferences, dietary restrictions, and "
            "dining patterns."
        ),
        expected_output=(
            "A concise natural-language user profile covering favorite cuisines, "
            "dietary restrictions, price sensitivity, and dining occasions."
        ),
        context="Raw visit_history and social_posts for the user.",
        dependencies=[],
    ),
    "RAG Retriever": AgentTask(
        description=(
            "Query the restaurant_articles and food_images vector collections using "
            "the user profile to retrieve relevant candidates."
        ),
        expected_output="Up to 20 candidate restaurants and recipes with similarity scores.",
        context="The user profile produced by the User Profile Generator.",
        dependencies=["User Profile Generator"],
    ),
    "Food Trend Analyst": AgentTask(
        description=(
            "Analyze the retrieved candidates for alignment with current food trends "
            "and emerging dining concepts."
        ),
        expected_output="A short trend analysis referencing specific candidates.",
        context="The user profile and retrieved candidates.",
        dependencies=["User Profile Generator", "RAG Retriever"],
    ),
    "Food Style Expert": AgentTask(
        description=(
            "Analyze the cuisine, cooking style, and flavor profile fit of the "
            "retrieved candidates against the user's preferences."
        ),
        expected_output="A short style/flavor analysis referencing specific candidates.",
        context="The user profile and retrieved candidates.",
        dependencies=["User Profile Generator", "RAG Retriever"],
    ),
    "Nutrition Expert": AgentTask(
        description=(
            "Evaluate the retrieved candidates for dietary compliance, allergens, and "
            "nutritional fit."
        ),
        expected_output=(
            "A short nutrition/dietary-compliance analysis referencing specific "
            "candidates, flagging any allergen risks."
        ),
        context="The user profile and retrieved candidates.",
        dependencies=["User Profile Generator", "RAG Retriever"],
    ),
    "Recommendation Expert": AgentTask(
        description=(
            "Synthesize the user profile, retrieved candidates, and the three "
            "analyses into a final top-5 restaurant and top-5 recipe recommendation "
            "list with explanations."
        ),
        expected_output="A ranked list of up to 5 restaurants and 5 recipes, each with a one-sentence explanation.",
        context="The user profile, retrieved candidates, and the trend/style/nutrition analyses.",
        dependencies=["Food Trend Analyst", "Food Style Expert", "Nutrition Expert"],
    ),
}


def _print_agent(persona: AgentPersona) -> None:
    print(f"Role: {persona.role}")
    print(f"Goal: {persona.goal}")
    print(f"Backstory: {persona.backstory}")
    task = TASKS.get(persona.name)
    if task:
        print(f"Task: {task.description}")
        print(f"Expected output: {task.expected_output}")


if __name__ == "__main__":
    for persona in ALL_PERSONAS:
        _print_agent(persona)
        print("-" * 60)
