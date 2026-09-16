from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters

credentials=Credentials(
    url="https://us-south.ml.cloud.ibm.com",
)

params=TextChatParameters(
    temperature=0.2,
    top_p=0.5,
    max_tokens=2000
)

model=ModelInference(
    model_id="meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
    credentials=credentials,
    project_id="skills-network",
    params=params
)
