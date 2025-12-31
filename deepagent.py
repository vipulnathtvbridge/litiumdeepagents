from dotenv import load_dotenv
load_dotenv()

from src.llms import get_model
from deepagents import create_deep_agent
from src.tools.todo_tools import *
from src.prompts.orchestrator import get_orchestrator_prompt

import os
import warnings

warnings.filterwarnings(
    "ignore",
    message="LangSmith now uses UUID v7",
    category=UserWarning,
)


model = get_model("reliable")
tools = [write_todos, read_todos]

# Use the orchestrator prompt from src/prompts/orchestrator.py
orchestrator_prompt = get_orchestrator_prompt()

agent = create_deep_agent(
    model=model,
    tools=tools,
    system_prompt=TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + orchestrator_prompt,
    state_schema = DeepAgentState
)


input_content = '''{
      "html_snippet": "<div class=\"flex items-center mb-3 mr-[490px] gap-3\">\n\t<span class=\"text-[#101010] text-sm font-bold\" >\n\t\tQuantity\n\t</span>\n\t<div class=\"flex items-center bg-white w-[107px] p-1.5\">\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/haz2vfmg_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 mr-[15px] object-fill\"\n\t\t/>\n\t\t<span class=\"text-black text-sm font-bold mr-[17px]\" >\n\t\t\t23\n\t\t</span>\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/8vm9znuj_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 object-fill\"\n\t\t/>\n\t</div>\n</div>\n\n<div class=\"flex items-center self-stretch mr-[11px]\">\n\t<div class=\"flex items-center bg-white w-[93px] p-[3px] mr-4\">\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/kegbawk5_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 mr-3 object-fill\"\n\t\t/>\n\t\t<span class=\"text-black text-sm font-bold mr-3.5\" >\n\t\t\t12\n\t\t</span>\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/no8kgd1v_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 object-fill\"\n\t\t/>\n\t</div>\n</div>",
      "target_component": "components/products/QuantityInput.tsx",
      "file": "create",
      "action": "Create reusable quantity control matching exact white box sizing and icon alignment for both product header and variants rows",
      "details": [
        "Props: value:number, onChange(next:number), className?, sizeVariant:'detail'|'variant' to switch between w-[107px] p-1.5 and w-[93px] p-[3px]",
        "Render left/right icon buttons (decrement/increment) with fixed w-6 h-6 and exact spacing (mr-[15px]/mr-3 etc.)",
        "Do not hardcode image URLs; accept icon assets via props or use inline SVGs while preserving dimensions",
        "Ensure keyboard accessibility: buttons with aria-label and disabled handling at min/max"
      ],
      "reference_files": [
        "components/products/VariantsTable.tsx",
        "components/products/ProductDetail.tsx"
      ],
      "implementation_step": 2
    }'''

result = agent.invoke(
    {"messages": 
    [{"role": "user", 
      "content": input_content}]
      })

# Print the agent's response
print(result["messages"][-1].content)
# display(Image(agent.get_graph(xray=True).draw_mermaid_png()))