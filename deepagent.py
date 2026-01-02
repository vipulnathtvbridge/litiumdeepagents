from dotenv import load_dotenv
load_dotenv()

from src.llms import get_model
from langchain.agents.middleware import TodoListMiddleware
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents import create_deep_agent, CompiledSubAgent

from src.tools.todo_tools import *
from src.prompts.orchestrator import get_orchestrator_prompt
from src.subagents.html_analyser import html_analyser_agent
from src.subagents.tsx_styling_agent import tsx_styling_agent

import os
import warnings
import logging

# Try to import BaseCallbackHandler from different possible locations
try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:
    try:
        from langchain_core.callbacks.base_callback import BaseCallbackHandler
    except ImportError:
        # Fallback: create a minimal callback handler
        class BaseCallbackHandler:
            pass


from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StateBackend
)


html_anlyser_subagent = CompiledSubAgent(
    name="html_analyser",
    description="agent specialized for suggesting styling changes" \
    " to tsx file based on html snippet and project tsx files",
    runnable=html_analyser_agent
)

tsx_styling_subagent = CompiledSubAgent(
    name="tsx_styling_agent",
    description="agent specialized for applying styling changes from the scratch pad" \
    " to tsx files by reading proposed diffs and executing modifications",
    runnable=tsx_styling_agent
)

subagents =[html_anlyser_subagent, tsx_styling_subagent]

def create_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),

        routes={
            "/agent/": FilesystemBackend(
                root_dir=os.path.abspath('C:/litiumdeepagents/ecom/trendcart'), virtual_mode=True
            ),

            "/project/": FilesystemBackend(
                root_dir=os.path.abspath("C:/ecommerce/trendcart/gleemart-fe"), virtual_mode=True
            )
        }
    )


# You must:
# - Use /agent/* only for logs, plans, or TODOs
# - Use /project/* only for UI styling changes
# - Never modify package.json, lock files, or config
# - Never write outside allowed directories


warnings.filterwarnings(
    "ignore",
    message="LangSmith now uses UUID v7",
    category=UserWarning,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Custom callback to print intermediate steps
class AgentDebugCallback(BaseCallbackHandler):
    """Custom callback handler for debugging agent execution"""

    def __init__(self):
        super().__init__()
        self.raise_error = False
        self.ignore_chain = False
        self.ignore_agent = False
        self.ignore_llm = False
        self.ignore_chat_model = False
        self.ignore_retriever = False
        self.ignore_tool = False
        self.ignore_custom_event = False

    def on_tool_start(self, serialized, input_str, **kwargs):
        print(f"\n🔧 TOOL CALLED: {serialized.get('name', 'unknown')}")
        print(f"   Input: {input_str}")

    def on_tool_end(self, output, **kwargs):
        output_str = str(output)
        print(f"✅ TOOL OUTPUT: {output_str[:200] if len(output_str) > 200 else output_str}")

    def on_tool_error(self, error, **kwargs):
        print(f"❌ TOOL ERROR: {error}")

    def on_agent_action(self, action, **kwargs):
        print(f"\n🤖 AGENT ACTION: {action.tool}")
        print(f"   Input: {action.tool_input}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        if isinstance(serialized, dict) and 'name' in serialized:
            print(f"\n▶️  CHAIN START: {serialized['name']}")

    def on_chain_end(self, outputs, **kwargs):
        if outputs:
            output_str = str(outputs)
            print(f"✅ CHAIN OUTPUT: {output_str[:200] if len(output_str) > 200 else output_str}")

    def on_text(self, text, **kwargs):
        if isinstance(text, str) and text.strip():
            print(f"\n💬 TEXT: {text}")


model = get_model("reliable")
# tools = [read_tsx]

# Use the orchestrator prompt from src/prompts/orchestrator.py
orchestrator_prompt = get_orchestrator_prompt()

agent = create_deep_agent(
    model=model,
    # tools=tools,
    system_prompt=orchestrator_prompt,
    backend = create_backend,

)


# input_content = '''{
#       "html_snippet": "<div class=\"flex items-center mb-3 mr-[490px] gap-3\">\n\t<span class=\"text-[#101010] text-sm font-bold\" >\n\t\tQuantity\n\t</span>\n\t<div class=\"flex items-center bg-white w-[107px] p-1.5\">\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/haz2vfmg_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 mr-[15px] object-fill\"\n\t\t/>\n\t\t<span class=\"text-black text-sm font-bold mr-[17px]\" >\n\t\t\t23\n\t\t</span>\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/8vm9znuj_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 object-fill\"\n\t\t/>\n\t</div>\n</div>\n\n<div class=\"flex items-center self-stretch mr-[11px]\">\n\t<div class=\"flex items-center bg-white w-[93px] p-[3px] mr-4\">\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/kegbawk5_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 mr-3 object-fill\"\n\t\t/>\n\t\t<span class=\"text-black text-sm font-bold mr-3.5\" >\n\t\t\t12\n\t\t</span>\n\t\t<img\n\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/no8kgd1v_expires_30_days.png\" \n\t\t\tclass=\"w-6 h-6 object-fill\"\n\t\t/>\n\t</div>\n</div>",
#       "target_component": "/project/components/products/QuantityInput.tsx",
#       "file": "create",
#       "action": "Create reusable quantity control matching exact white box sizing and icon alignment for both product header and variants rows",
#       "details": [
#         "Props: value:number, onChange(next:number), className?, sizeVariant:'detail'|'variant' to switch between w-[107px] p-1.5 and w-[93px] p-[3px]",
#         "Render left/right icon buttons (decrement/increment) with fixed w-6 h-6 and exact spacing (mr-[15px]/mr-3 etc.)",
#         "Do not hardcode image URLs; accept icon assets via props or use inline SVGs while preserving dimensions",
#         "Ensure keyboard accessibility: buttons with aria-label and disabled handling at min/max"
#       ],
#       "reference_files": [
#         "/project/components/products/VariantsTable.tsx",
#         "/project/components/products/ProductDetail.tsx"
#       ],
#       "implementation_step": 2
#     }'''

input_content='''{
      "html_snippet": "<div class=\"items-start bg-white\">\n\t\t<div class=\"flex flex-col w-[1512px] p-[50px] gap-[50px]\">\n\t\t\t<div class=\"flex items-start self-stretch gap-[15px]\">\n\t\t\t\t<div class=\"flex items-start w-[698px] gap-[15px]\">\n\t\t\t\t\t<img\n\t\t\t\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/b02zk04a_expires_30_days.png\" \n\t\t\t\t\t\tclass=\"w-[104px] h-[467px] object-fill\"\n\t\t\t\t\t/>\n\t\t\t\t\t<div class=\"flex justify-between items-start bg-[url('https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/unhvltgw_expires_30_days.png')] bg-cover bg-center w-[579px] pt-[19px] pb-[502px] px-[18px]\">\n\t\t\t\t\t\t<div class=\"flex flex-col items-start bg-[#1A2332B0] w-[94px] py-[3px] px-2\">\n\t\t\t\t\t\t\t<span class=\"text-white text-sm font-bold\" >\n\t\t\t\t\t\t\t\tSpecial Offer!\n\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t</div>\n\t\t\t\t\t\t<div class=\"flex items-center bg-[#E8FF00] w-[179px] py-[11px] px-4 gap-2\">\n\t\t\t\t\t\t\t<img\n\t\t\t\t\t\t\t\tsrc=\"https://storage.googleapis.com/tagjs-prod.appspot.com/v1/nmdDMp2Obk/te3471aa_expires_30_days.png\" \n\t\t\t\t\t\t\t\tclass=\"w-[17px] h-[13px] object-fill\"\n\t\t\t\t\t\t\t/>\n\t\t\t\t\t\t\t<span class=\"text-[#1A2332] text-sm font-bold\" >\n\t\t\t\t\t\t\t\tConfigure Product\n\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t</div>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t\t<div class=\"flex flex-col items-start bg-[#F8F6F2] w-[698px] py-8 pl-8\">\n\t\t\t\t\t<!-- product info panel -->\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n\t</div>",
      "target_component": "app/(content)/(StickyHeader)/ProductWithVariantsProduct/[[...slug]]/page.tsx",
      "file": "edit",
      "action": "Implement fixed-width canvas container and delegate rendering to updated ProductDetail layout matching the HTML page structure",
      "details": [
        "Wrap content in bg-white root and a fixed canvas container: w-[1512px] p-[50px] gap-[50px] flex flex-col",
        "Ensure ProductDetail is placed as the single child inside this canvas to control spacing between major sections",
        "Keep server data fetching unchanged; only adjust layout wrapper/structure around <ProductDetail />",
        "If current ProductDetail already has its own container, remove/disable internal max-width constraints to avoid double-centering"
      ],
      "reference_files": [
        "components/products/ProductDetail.tsx"
      ],
      "implementation_step": 9
    }'''

print("=" * 80)
print("🚀 STARTING DEEP AGENT EXECUTION")
print("=" * 80)

# Create callback handler
debug_callback = AgentDebugCallback()

# Invoke agent with callbacks
result = agent.invoke(
    {"messages":
    [{"role": "user",
      "content": input_content}]
    },
    config={"callbacks": [debug_callback]}
)

# Print all messages from the agent
print("\n" + "=" * 80)
print("📝 AGENT CONVERSATION HISTORY")
print("=" * 80)
for i, msg in enumerate(result["messages"]):
    print(f"\n[Message {i}] Role: {msg.get('role', 'unknown')}")
    content = msg.get('content', '')
    if isinstance(content, str):
        print(f"Content: {content[:500]}{'...' if len(content) > 500 else ''}")
    else:
        print(f"Content: {content}")

# Print the final response
print("\n" + "=" * 80)
print("✨ FINAL AGENT RESPONSE")
print("=" * 80)
print(result["messages"][-1].content)
# display(Image(agent.get_graph(xray=True).draw_mermaid_png()))