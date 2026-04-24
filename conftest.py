# ============================================================
# 文件说明：Pytest全局配置文件（conftest.py）
# 作用：定义所有测试用例共享的Fixture
# 重要说明：该系统的Token机制为"单点登录"，即同一账号每次登录
#          会生成新Token并使旧Token失效。因此：
#          1. 全局只登录一次，所有用例共享同一个Token
#          2. test_login.py中的登录测试使用独立的账号或放在最后执行
# ============================================================

import sys
import os

# 将项目根目录添加到Python模块搜索路径
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import allure
from api.login_api import LoginApi
from config.settings import LOGIN_ACCOUNT, LOGIN_PASSWORD
from utils.log_util import logger


# 使用模块级变量缓存Token，避免重复登录导致Token失效
_cached_token = None
_cached_login_data = None


def _do_login():
    """执行登录并缓存结果"""
    global _cached_token, _cached_login_data

    logger.info("=" * 60)
    logger.info("【全局前置】开始执行登录，获取认证Token...")
    logger.info("=" * 60)

    login_api = LoginApi()
    result = login_api.login(account=LOGIN_ACCOUNT, password=LOGIN_PASSWORD)

    if not result:
        pytest.fail(
            "登录失败！无法获取Token。"
            "请检查：1.服务器是否可访问 2.账号密码是否正确 3.登录接口是否正常"
        )

    _cached_token = result["userToken"]
    _cached_login_data = result
    logger.info(f"【全局前置】登录成功，用户: {result.get('realName')}, Token: {_cached_token}")
    return result


@pytest.fixture(scope="session")
def login_data():
    """
    全局登录Fixture：在所有测试用例执行前，调用登录接口获取Token和用户信息。

    scope="session" 表示整个测试会话只执行一次。

    返回:
        dict: 包含 userToken、userId、agentId 等登录信息
    """
    global _cached_login_data
    if _cached_login_data is None:
        _do_login()

    yield _cached_login_data

    logger.info("=" * 60)
    logger.info("【全局后置】所有测试用例执行完毕")
    logger.info("=" * 60)


@pytest.fixture(scope="session")
def login_token(login_data):
    """
    便捷Fixture：直接返回userToken字符串。

    大多数测试用例只需要Token来初始化API类，用这个Fixture更方便。
    """
    return login_data["userToken"]


def pytest_collection_modifyitems(items):
    """
    Pytest钩子函数：调整测试用例的执行顺序。

    策略：将test_login.py中的用例放到最后执行，
    因为登录测试中的错误密码/空密码等测试可能会影响当前会话的Token。
    """
    login_tests = []
    other_tests = []

    for item in items:
        if "test_login" in item.nodeid:
            login_tests.append(item)
        else:
            other_tests.append(item)

    # 先执行业务接口测试，最后执行登录测试
    items[:] = other_tests + login_tests
