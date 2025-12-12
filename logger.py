import logging
import os

def setup_logger(name="AgentSystem", log_file="agent_trace.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 清除旧的 handlers 避免重复
    if logger.hasHandlers():
        logger.handlers.clear()

    # 1. 文件输出 (详细，用于写报告)
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    # 格式：时间 - 角色 - 级别 - 消息
    file_formatter = logging.Formatter('%(asctime)s - [%(name)s] - %(levelname)s - \n%(message)s\n' + '-'*30)
    file_handler.setFormatter(file_formatter)
    
    # 2. 控制台输出 (简洁，用于看进度)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('[%(name)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 全局单例 logger
system_logger = setup_logger()