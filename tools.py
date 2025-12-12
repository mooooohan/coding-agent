import os
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from config import WORK_DIR
from logger import system_logger

def write_to_file(filename, content):
    """写入文件到 workspace"""
    filepath = os.path.join(WORK_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    system_logger.info(f"FileSystem: Wrote to {filename}")
    return f"Successfully wrote to {filename}"

def read_file(filename):
    """读取 workspace 中的文件"""
    filepath = os.path.join(WORK_DIR, filename)
    if not os.path.exists(filepath):
        return f"Error: File {filename} not found."
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def execute_command(command):
    """执行 Shell 命令"""
    system_logger.info(f"Shell: Executing '{command}'")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=WORK_DIR, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return f"Command executed.\nOutput:\n{output}"
    except Exception as e:
        return f"Execution error: {str(e)}"

def fetch_arxiv_papers(category, max_results=5):
    """
    [REAL DATA] 调用 arXiv API 获取真实论文数据。
    Args:
        category: arXiv 类别，例如 'cs.AI', 'cs.CV', 'cs.SE'
    """
    system_logger.info(f"ArXiv: Fetching real papers for {category}...")
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            
        # 解析 XML
        root = ET.fromstring(data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        papers = []
        
        for entry in root.findall('atom:entry', namespace):
            title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
            published = entry.find('atom:published', namespace).text
            summary = entry.find('atom:summary', namespace).text.replace('\n', ' ').strip()[:200] + "..."
            link = entry.find('atom:id', namespace).text
            
            # 提取作者
            authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
            
            papers.append(f"Title: {title}\nDate: {published}\nAuthors: {', '.join(authors)}\nLink: {link}\nSummary: {summary}\n---")
            
        return "\n".join(papers)
    except Exception as e:
        return f"ArXiv API Error: {e}"

# 工具注册表
AVAILABLE_TOOLS = {
    "write_to_file": write_to_file,
    "read_file": read_file,
    "execute_command": execute_command,
    "fetch_arxiv_papers": fetch_arxiv_papers # 这里的工具能够抓取真数据
}