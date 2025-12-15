import os
import json
from agent import Agent
from prompts import PLANNER_PROMPT, CODER_PROMPT, REVIEWER_PROMPT
from utils import clean_and_parse_json
from tools import read_file
from logger import system_logger

def main():
    print("=== Qwen-Powered Real-Data Code Agent ===")
    system_logger.info("System Started")
    
    # 1. 初始化智能体
    planner = Agent("Planner", PLANNER_PROMPT)
    coder = Agent("Coder", CODER_PROMPT)
    reviewer = Agent("Reviewer", REVIEWER_PROMPT)
    
    # 2. 详细的任务描述 (强调真实数据)
    task_description = """
    Build an 'arXiv CS Daily' webpage using Python Flask.
    Requirements:
    1. A script (e.g., data_fetcher.py) that uses the 'fetch_arxiv_papers' tool to get REAL papers for categories: cs.AI, cs.CV, cs.SE.
    2. Save the fetched data into a JSON file (e.g., papers.json).
    3. A Flask app (app.py) that reads papers.json and displays them.
    4. The Homepage should list papers with titles and dates.
    5. A Detail page showing the abstract/summary and link.
    6. Navigation menu to filter by category.
    """
    
    # 3. 规划阶段
    print("\n>>> Phase 1: Planning")
    plan_response = planner.chat(task_description)
    task_list = clean_and_parse_json(plan_response)
    
    if not task_list or not isinstance(task_list, list):
        print("Error: Planner failed to generate valid JSON.")
        return

    print(f"Plan generated with {len(task_list)} steps.")
    system_logger.info(f"Plan: {json.dumps(task_list, indent=2)}")

    # 4. 执行循环
    for task_item in task_list:
        task_id = task_item.get('id')
        task_desc = task_item.get('task')
        
        print(f"\n==================================================")
        print(f"Task {task_id}: {task_desc}")
        print(f"==================================================")
        
        max_retries = 3
        retry_count = 0
        task_passed = False
        
        while retry_count < max_retries and not task_passed:
            # Context Management: 每次任务开始前，注入当前文件状态
            # 这能防止 Agent 在长任务中“迷失”
            import os
            from config import WORK_DIR
            existing_files = []
            if os.path.exists(WORK_DIR):
                existing_files = os.listdir(WORK_DIR)
                
            # 重置 Coder 记忆，只保留 System Prompt 和 Context
            coder.messages = [
                {"role": "system", "content": CODER_PROMPT},
                {"role": "user", "content": f"Current workspace files: {existing_files}. \nYour Task: {task_desc}. \nIf previous attempts failed, fix them."}
            ]
            
            # Coder 执行
            print(f"\n[Coder] Working (Attempt {retry_count+1})...")
            coder.chat("Start working.")
            
            # Reviewer 检查
            print(f"\n[Reviewer] Checking...")
            
            # 自动读取关键代码内容供 Reviewer 检查 (RAG-lite)
            code_context = ""
            from config import WORK_DIR
            for f in existing_files:
                if f.endswith('.py') or f.endswith('.html') or f.endswith('.json'):
                    # 使用正确的路径读取文件
                    try:
                        import os
                        with open(os.path.join(WORK_DIR, f), 'r', encoding='utf-8') as file:
                            content = file.read()
                        code_context += f"\nFile: {f}\nContent:\n{content[:1000]}...\n" # 截断以节省 token
                    except Exception as e:
                        code_context += f"\nFile: {f}\nError: {str(e)}\n"
            
            review_msg = f"Task was: {task_desc}. Check the file contents below. Does it look correct and use REAL data logic? Output PASS or FAIL.\n{code_context}"
            review_response = reviewer.chat(review_msg)
            
            if "PASS" in review_response.upper():
                print(f"✅ Task {task_id} Passed.")
                task_passed = True
            else:
                print(f"❌ Task {task_id} Failed. Reason: {review_response}")
                retry_count += 1
        
        if not task_passed:
            print(f"⚠️ Warning: Task {task_id} skipped after retries.")

    print("\n=== Project Complete ===")
    print("Run the app in 'workspace/': python app.py")

if __name__ == "__main__":
    main()