import os
from openai import OpenAI

# ==========================================
# 阿里云 Qwen 配置 (DashScope)
# ==========================================
# 替换为你的真实 API Key
API_KEY = "sk-55b426b1961a4de9a639eb7dd8567a65" 

# 阿里云兼容 OpenAI 的 Base URL
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

MODEL_NAME = "qwen3-coder-plus" 

# 工作目录：Agent 生成的代码将放在这里
WORK_DIR = "workspace-test"
if not os.path.exists(WORK_DIR):
    os.makedirs(WORK_DIR)

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def get_chat_completion(messages, temperature=0.5):
    """
    封装 LLM API 调用
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[API Error]: {e}")
        return None