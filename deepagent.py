from dotenv import load_dotenv
load_dotenv()

from src.llms import get_model
from deepagents import create_deep_agent
from src.tools.websearch import hr_search
import os


import warnings

warnings.filterwarnings(
    "ignore",
    message="LangSmith now uses UUID v7", 
    category=UserWarning,
)


model = get_model("reliable")
# agent = create_deep_agent(model=model)



# System prompt to steer the agent to be an expert researcher
edit_instructions = """You are an expert Next js app 
Styling orchestrator agent who have long term experience in Litium based ecommerce platfrom.
You task is to overlooks the styling of the next js pages and its components.
You will be given a json which contains html snippet {}  that is being collected from figma design,
you will be given the files to majorly cross reference to make this changes happen {} along 
with the base page {} where these components are called.
"""

agent = create_deep_agent(
    model=model,
    tools=[hr_search],
    system_prompt=edit_instructions
)


result = agent.invoke(
    {"messages": 
    [{"role": "user", 
      "content": "Where did vipulnath complete his btech"}]
      })

# Print the agent's response
print(result["messages"][-1].content)