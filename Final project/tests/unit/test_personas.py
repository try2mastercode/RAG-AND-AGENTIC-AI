from agents.personas import ALL_PERSONAS, FOOD_STYLE_EXPERT, TASKS


def test_all_six_agents_defined():
    assert len(ALL_PERSONAS) == 6
    names = {p.name for p in ALL_PERSONAS}
    assert names == {
        "User Profile Generator",
        "RAG Retriever",
        "Food Trend Analyst",
        "Food Style Expert",
        "Nutrition Expert",
        "Recommendation Expert",
    }


def test_every_persona_has_role_goal_backstory():
    for persona in ALL_PERSONAS:
        assert persona.role
        assert persona.goal
        assert persona.backstory


def test_food_style_expert_fields():
    assert FOOD_STYLE_EXPERT.role == "Food Style Expert"
    assert "cuisine" in FOOD_STYLE_EXPERT.goal.lower()
    assert "chef" in FOOD_STYLE_EXPERT.backstory.lower()


def test_every_persona_has_a_task_with_dependencies_tracked():
    for persona in ALL_PERSONAS:
        task = TASKS[persona.name]
        assert task.description
        assert task.expected_output


def test_recommendation_expert_depends_on_the_three_analysis_agents():
    task = TASKS["Recommendation Expert"]
    assert set(task.dependencies) == {"Food Trend Analyst", "Food Style Expert", "Nutrition Expert"}
