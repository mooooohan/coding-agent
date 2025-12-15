import os
import json
import sys
import subprocess
from openai import OpenAI

# ==========================================
# 1. 配置区域 (Configuration)
# ==========================================

API_KEY = "sk-55b426b1961a4de9a639eb7dd8567a65" 

BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-flash"

try:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    sys.exit(1)

WORKSPACE_DIR = "workspace_arxiv"

# ==========================================
# 2. 工具定义 (Tools Implementation)
# ==========================================

def write_to_file(filename, content):
    """创建或覆盖文件"""
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def read_file(filename):
    """读取文件内容"""
    filepath = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(filepath):
        return f"File {filename} not found."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files():
    """列出文件列表"""
    if not os.path.exists(WORKSPACE_DIR):
        return "Workspace directory does not exist yet."
    files_list = []
    for root, _, filenames in os.walk(WORKSPACE_DIR):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), WORKSPACE_DIR)
            files_list.append(rel_path)
    return json.dumps(files_list)

def execute_command(command):
    """
    [关键升级] 执行 Shell 命令。
    允许 Agent 运行 pip install 或 python script.py 来抓取真实数据。
    """
    print(f"   ⚡ 执行系统命令: {command}")
    try:
        # 为了安全，限制在工作区目录执行（虽然 subprocess 仍然有风险，但在作业环境中通常允许）
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=WORKSPACE_DIR if os.path.exists(WORKSPACE_DIR) else ".",
            capture_output=True, 
            text=True,
            timeout=30 # 防止脚本卡死
        )
        output = result.stdout + result.stderr
        return output if output.strip() else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {str(e)}"

# 工具映射
available_tools = {
    "write_to_file": write_to_file,
    "read_file": read_file,
    "list_files": list_files,
    "execute_command": execute_command
}

# 工具 Schema
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "Write code to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Filename (e.g., fetch_data.py)"},
                    "content": {"type": "string", "description": "Code content"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in workspace.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a shell command. Use this to run python scripts or install dependencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to run (e.g., 'python fetch_data.py')"}
                },
                "required": ["command"]
            }
        }
    }
]

# ==========================================
# 3. Agent 类 (支持多轮对话与工具循环)
# ==========================================

class Agent:
    def __init__(self, name, system_prompt, model=MODEL_NAME):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]

    def chat(self, user_input, max_turns=5):
        """
        max_turns: 防止工具调用陷入死循环
        """
        self.messages.append({"role": "user", "content": user_input})
        print(f"\n🔵 [{self.name}] 正在思考...")

        turn_count = 0
        while turn_count < max_turns:
            turn_count += 1
            
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=tools_schema,
                    tool_choice="auto"
                )
                
                msg = response.choices[0].message
                self.messages.append(msg)

                if msg.tool_calls:
                    print(f"   ⚙️ [{self.name}] 决定调用工具 (Round {turn_count})...")
                    
                    for tool_call in msg.tool_calls:
                        func_name = tool_call.function.name
                        args_str = tool_call.function.arguments
                        
                        try:
                            args = json.loads(args_str)
                            print(f"      > 调用: {func_name} ({args.get('filename') or args.get('command')})")
                            
                            if func_name in available_tools:
                                tool_result = available_tools[func_name](**args)
                            else:
                                tool_result = f"Error: Tool {func_name} not found."
                                
                        except Exception as e:
                            tool_result = f"Error parsing/executing: {str(e)}"

                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": str(tool_result)
                        })
                    
                    # 工具执行完，继续循环，让 LLM 看到结果后决定下一步
                else:
                    # 没有工具调用，说明 LLM 完成了这一轮的回复
                    return msg.content

            except Exception as e:
                return f"❌ API Error: {str(e)}"
        
        return "⚠️ Max turns reached. Task may be incomplete."

# ==========================================
# 4. 高级 Prompt (High-Quality Real Data)
# ==========================================

PLANNER_PROMPT = """
You are the Technical Lead and Architect.
Your goal is to design a robust web application that fetches REAL DATA from the arXiv API.

1.  **Architecture**:
    -   We cannot fetch arXiv data directly in browser JS due to CORS.
    -   **Solution**: Design a 'Data Fetcher' Python script (`fetch_data.py`) that runs locally, fetches XML from arXiv, parses it, and saves it as a JavaScript file (`data.js`).
    -   The `data.js` should assign the data to a global variable (e.g., `window.arxivData = [...]`) so `index.html` can load it without CORS errors.
    
2.  **Task Breakdown**:
    -   Step 1: Write `fetch_data.py` (Python) to query `http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CV&start=0&max_results=10`. Parse the XML response.
    -   Step 2: Execute `fetch_data.py` to generate the real data file.
    -   Step 3: Create `index.html` (Bootstrap UI) that reads the data and renders the list.
    
3.  **Output**: Provide a precise step-by-step plan for the Coder.
"""

CODER_PROMPT = """
You are the Full-Stack Engineer. 
Your goal is to implement the code AND execute it to ensure real data is obtained.

1.  **Strict NO MOCK DATA policy**: You must write a Python script to fetch data from `http://export.arxiv.org/api/query`.
2.  **Handling arXiv XML**: The API returns Atom/XML. Use standard `xml.etree.ElementTree` or `urllib` to parse it. Do NOT assume it is JSON.
3.  **The CORS Solution**: 
    -   Save the fetched data into a file named `data.js`.
    -   Format the file content as: `window.arxivData = [ ... json data ... ];`
    -   This allows `index.html` to include `<script src="data.js"></script>` and access `window.arxivData` immediately.
4.  **Action Sequence**:
    -   Write `fetch_data.py`.
    -   **IMMEDIATELY USE `execute_command`** to run `python fetch_data.py`. 
    -   Check if `data.js` exists.
    -   Then write `index.html` and `style.css`.
5.  **UI Requirements**: Use Bootstrap 5 via CDN for a professional look.
"""

# ==========================================
# 5. 主程序
# ==========================================

def main():
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    planner = Agent("Planner", PLANNER_PROMPT, model=MODEL_NAME)
    coder = Agent("Coder", CODER_PROMPT, model=MODEL_NAME)

    # 用户的任务描述 - 强调真实数据
    user_task = """
    Create a 'arXiv CS Daily' website using REAL data.
    
    Requirements:
    1.  **Real Data**: Fetch the latest 10 papers for 'cs.AI' and 'cs.CV' from arXiv.org API.
    2.  **Display**: Show Title, Authors, Published Date, and a link to the PDF.
    3.  **Tech**: HTML, CSS, and a Python script for data fetching.
    4.  **Automation**: You must execute the script to verify data is downloaded.
    """

    print("="*60)
    print("🚀 AutoDev Agent System: arXiv Real-Data Edition")
    print("="*60)

    # --- Phase 1: Planning ---
    print(f"\n>>> [Phase 1] Architecture Planning")
    plan = planner.chat(f"Requirement: {user_task}")
    print(f"\n📋 Plan:\n{plan}")

    # --- Phase 2: Implementation & Execution ---
    print(f"\n>>> [Phase 2] Coding & Data Fetching")
    
    # 我们把计划传给程序员，并强制它执行
    coder_instruction = f"""
    Follow this plan strictly:
    {plan}
    
    CRITICAL: 
    1. Write the `fetch_data.py` script to handle arXiv XML response.
    2. RUN the script using `execute_command` to generate `data.js`.
    3. Only after data is ready, create the `index.html`.
    """
    
    result = coder.chat(coder_instruction, max_turns=10) # 给予更多回合数以允许运行命令
    print(f"\n💻 Final Report:\n{result}")

    print("\n" + "="*60)
    print("✅ Project Completed.")
    print(f"1. Check '{WORKSPACE_DIR}/data.js' to see real arXiv data.")
    print(f"2. Open '{WORKSPACE_DIR}/index.html' in your browser.")
    print("="*60)

if __name__ == "__main__":
    main()