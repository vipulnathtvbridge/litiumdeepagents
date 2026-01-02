from dotenv import load_dotenv
load_dotenv()

from src.llms import get_model
from langchain.agents import create_agent
from src.prompts.html_analyser import get_html_analyser_prompt
from src.prompts.prompts import TODO_USAGE_INSTRUCTIONS
from src.state import DeepAgentState
from src.tools.tsx_tools import read_tsx, write_tsx
from src.tools.scratch_pad_tools import write_scratch_pad, read_scratch_pad

import os
import warnings

warnings.filterwarnings(
    "ignore",
    message="LangSmith now uses UUID v7",
    category=UserWarning,
)


model = get_model("reliable")

# Configure tools for HTML analyzer agent
tools = [
    read_tsx,
    write_scratch_pad,
    read_scratch_pad,
]

# Get the HTML analyzer prompt
html_analyser_prompt = get_html_analyser_prompt()

html_analyser_agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=html_analyser_prompt,
    state_schema=DeepAgentState,
)


if __name__ == "__main__":

    input_content = '''{
        "html_snippet": "<span class=\\"text-[#1A2332] text-sm font-bold mb-3 mr-[459px]\\" >\\n\\tPer piece 3,500 SEK 4500 SEK\\n</span>\\n\\n<div class=\\"flex items-center self-stretch\\">\\n\\t<span class=\\"text-[#1A2332] text-base font-bold mr-[11px]\\" >\\n\\t\\tFrom 2,300 SEK\\n\\t</span>\\n\\t<span class=\\"text-[#101010] text-xs font-bold mr-[5px]\\" >\\n\\t\\t4,000 SEK\\n\\t</span>\\n\\t<img\\n\\t\\tsrc=\\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/3rs02mfw_expires_30_days.png\\" \\n\\t\\tclass=\\"w-3 h-[15px] object-fill\\"\\n\\t/>\\n\\t<span class=\\"text-[#4F8D56] text-xs font-bold\\" >\\n\\t\\t25%\\n\\t</span>\\n</div>",
        "target_component": "components/products/ProductPrice.tsx",
        "file": "edit",
        "action": "Support HTML-specific price compositions: 'Per piece' line and 'From' pricing with old price + discount percent indicator",
        "details": [
            "Add optional props to render: prefixLabel (e.g., 'Per piece'/'From'), showDiscountPercent (boolean), discountPercentOverride? (string)",
            "Match typography variants used in HTML: new price can be text-base font-bold; old price text-xs font-bold with line-through (or provided asset divider if required)",
            "Use existing VAT logic as-is; only change presentation and allow dual-format rendering",
            "Keep colors: main price text-brand-black, old price text-[#101010]/secondary as needed, percent text-stock-green"
        ],
        "reference_files": [
            "components/products/ProductCard.tsx",
            "components/products/ProductDetail.tsx"
        ],
        "implementation_step": 3
    }'''

    result = html_analyser_agent .invoke(
        {"messages":
        [{"role": "user",
        "content": input_content}]
        })

    # Print the agent's response
    print(result["messages"][-1].content)
