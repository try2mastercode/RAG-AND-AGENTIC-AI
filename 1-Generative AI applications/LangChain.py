from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain, SequentialChain

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# chain 1
template = "Your job is to suggest the classic dish from {location}. Your response:"
prompt_template = PromptTemplate(template=template, input_variables=['location'])
location_chain = LLMChain(llm=llm, prompt=prompt_template, output_key='meal')

# chain 2
template = "Given a {meal}, give a short and simple recipe on how to make this dish at home. Your response:"
prompt_template = PromptTemplate(template=template, input_variables=['meal'])
dish_chain = LLMChain(llm=llm, prompt=prompt_template, output_key='recipe')

# chain 3
template = "Given the recipe {recipe}, estimate how much time I need to cook it. Your response:"
prompt_template = PromptTemplate(template=template, input_variables=['recipe'])
recipe_chain = LLMChain(llm=llm, prompt=prompt_template, output_key='time')

# overall chain
overall_chain = SequentialChain(
    chains=[location_chain, dish_chain, recipe_chain],
    input_variables=["location"],
    output_variables=["meal", "recipe", "time"],
    verbose=True
)

result = overall_chain.invoke(input={'location': 'France'})
print(result)
