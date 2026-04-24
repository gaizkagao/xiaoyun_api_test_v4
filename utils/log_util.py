# ============================================================
# 文件说明：日志工具模块
# 作用：统一管理日志输出，同时输出到控制台和文件
# ============================================================

import logging
import os
from datetime import datetime

# 日志文件存放目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件名（按日期命名）
LOG_FILE = os.path.join(LOG_DIR, f"api_test_{datetime.now().strftime('%Y%m%d')}.log")


def get_logger(name="xiaoyun_api_test"):
    """获取日志记录器"""
    _logger = logging.getLogger(name)

    if not _logger.handlers:
        _logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)

        # 文件输出
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)

    return _logger


# 创建全局logger实例，其他模块直接导入使用
logger = get_logger()
