from dotenv import load_dotenv
load_dotenv()

from src.llms import get_model
from langchain.agents import create_agent
from src.prompts.tsx_styling_agent import get_tsx_styling_agent_prompt
from src.state import DeepAgentState
from src.tools.tsx_tools import read_tsx, write_tsx
from src.tools.scratch_pad_tools import read_scratch_pad

import os
import warnings

warnings.filterwarnings(
    "ignore",
    message="LangSmith now uses UUID v7",
    category=UserWarning,
)


model = get_model("smart")

# Configure tools for TSX Styling agent
tools = [
    read_scratch_pad,
    read_tsx,
    write_tsx,
]

# Get the TSX Styling agent prompt
tsx_styling_agent_prompt = get_tsx_styling_agent_prompt()

tsx_styling_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=tsx_styling_agent_prompt,
    state_schema=DeepAgentState,
)


if __name__ == "__main__":

    input_content = '''{
        "scratch_pad_review": true,
        "message": "Please read the scratch pad and apply all proposed changes to the TSX files"
    }'''

    result = tsx_styling_agent.invoke(
        {"messages":
        [{"role": "user",
        "content": input_content}]
        })

    # Print the agent's response
    print(result["messages"][-1].content)
