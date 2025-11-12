from typing import Optional
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any
from copy import deepcopy


# --- Define the Callback Function ---
def validate_tool_response(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Inspects/modifies the tool result after execution."""
    print(f"\n=========================== After TOOL Callback ===========================\n")
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Args used: {args}")
    print(f"[Callback] Original tool_response: {tool_response}")

    # Default structure for function tool results is {"result": <return_value>}
    tool_res = tool_response.get("result", "")
    # original_result_value = tool_response

    # --- Modification Example ---
    if tool_name == 'fetch_count':
        print("[Callback] Fetch Tool Detected.")
        if tool_res == 0:
            tool_context.state.update({"no_stock_note": True})
    else:
        tool_context.state.update({"no_stock_note": False})
    return None