from config import get_chat_completion
from tools import AVAILABLE_TOOLS
from utils import clean_and_parse_json
from logger import system_logger

class Agent:
    def __init__(self, name, role_prompt):
        self.name = name
        self.system_prompt = role_prompt
        self.messages = [{"role": "system", "content": role_prompt}]

    def chat(self, user_input, max_turns=8):
        """
        Agent 主循环，支持自动工具调用
        """
        self.messages.append({"role": "user", "content": user_input})
        system_logger.info(f"[{self.name}] User Input: {user_input[:200]}...")
        
        turn_count = 0
        while turn_count < max_turns:
            turn_count += 1
            
            # 调用 LLM
            response = get_chat_completion(self.messages)
            if not response:
                return "Error: API No Response"
            
            system_logger.debug(f"[{self.name}] Raw Response: {response}")

            # 解析工具调用
            tool_data = clean_and_parse_json(response)
            
            # 判断是否调用工具
            if tool_data and isinstance(tool_data, dict) and "tool" in tool_data:
                tool_name = tool_data.get("tool")
                args = tool_data.get("args", {})
                
                print(f"  > [{self.name}] Action: {tool_name} ...")
                system_logger.info(f"[{self.name}] Tool Call: {tool_name} Args: {args}")
                
                if tool_name in AVAILABLE_TOOLS:
                    try:
                        # 执行工具
                        result = AVAILABLE_TOOLS[tool_name](**args)
                    except Exception as e:
                        result = f"Tool Execution Error: {str(e)}"
                    
                    # 结果反馈
                    # 将结果截断一点以免撑爆 Context，但在日志中保留全量
                    display_result = result[:1000] + "...(truncated)" if len(result) > 1000 else result
                    
                    self.messages.append({"role": "assistant", "content": response})
                    self.messages.append({"role": "user", "content": f"Tool '{tool_name}' Output:\n{display_result}"})
                    
                    continue # 继续循环，让 Agent 决定下一步
                else:
                    self.messages.append({"role": "user", "content": f"Error: Tool {tool_name} not found."})
            
            else:
                # 最终回复
                self.messages.append({"role": "assistant", "content": response})
                print(f"[{self.name}] Finished turn.")
                return response
        
        return "Error: Maximum autonomous turns reached."