import json
import re

def clean_and_parse_json(text):
    """
    鲁棒的 JSON 解析器，能处理 Markdown 代码块和非标准格式。
    """
    if not text:
        return None
        
    try:
        # 1. 尝试直接解析
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. 尝试提取 ```json ... ``` 内部的内容
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
            
    # 3. 尝试提取列表 [...]
    match_list = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match_list:
        try:
            return json.loads(match_list.group(1))
        except:
            pass

    # 4. 暴力查找第一个 { 或 [
    try:
        start_brace = text.find("{")
        start_bracket = text.find("[")
        
        if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
            end = text.rfind("}")
            return json.loads(text[start_brace:end+1])
        elif start_bracket != -1:
            end = text.rfind("]")
            return json.loads(text[start_bracket:end+1])
    except:
        pass

    return None