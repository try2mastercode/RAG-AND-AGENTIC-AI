import config


def test_project_root_resolves():
    assert config.PROJECT_ROOT.name == "Final project"


def test_data_directories_exist():
    for d in [
        config.RAW_DIR,
        config.STRUCTURED_DIR,
        config.RECIPES_DIR,
        config.IMAGES_DIR,
        config.REVIEWS_DIR,
        config.CHROMA_DIR,
    ]:
        assert d.exists(), f"missing directory: {d}"


def test_groq_api_key_is_configured():
    assert config.GROQ_API_KEY, "GROQ_API_KEY not loaded from .env"


def test_collection_names_match_ibm_requirements():
    assert config.RESTAURANT_ARTICLES_COLLECTION == "restaurant_articles"
    assert config.FOOD_IMAGES_COLLECTION == "food_images"


def test_embedding_dimensions_match_ibm_requirements():
    assert config.TEXT_EMBEDDING_DIM == 384
    assert config.IMAGE_EMBEDDING_DIM == 512
