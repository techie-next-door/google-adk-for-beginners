from typing import Optional
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any
import json


def validate_tool_args(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"\n=========================== Before TOOL Callback ===========================\n")
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Original args: {args}")

    if tool_name == 'update_groceries':
        if isinstance(args, dict):
            print(f"[Callback] Args are as expected: {args}")
            return None
        else:
            try:
                print(f"[Callback] Debugging Args - {json.dumps(args)}")
            except Exception as e:
                print(f"[Callback] Issue in Args - {e}")
            return {"error": e}
