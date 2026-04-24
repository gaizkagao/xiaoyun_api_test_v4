# ============================================================
# 文件说明：登录接口测试用例
# 作用：验证登录接口的正向和逆向场景
# ============================================================

import allure
import pytest
from api.login_api import LoginApi
from config.settings import LOGIN_ACCOUNT, LOGIN_PASSWORD


@allure.epic("小云云地接")
@allure.feature("登录模块")
class TestLogin:
    """登录接口测试类"""

    @allure.story("密码登录")
    @allure.title("正向-使用正确账号密码登录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self):
        """验证使用正确的账号密码可以成功登录并返回Token"""
        login_api = LoginApi()
        result = login_api.login(account=LOGIN_ACCOUNT, password=LOGIN_PASSWORD)

        # 断言登录成功
        assert result is not None, "登录返回结果不应为None"
        assert result.get("userToken"), "登录应返回有效的userToken"
        assert len(result["userToken"]) > 0, "userToken不应为空字符串"

        # 断言返回了必要的用户信息
        assert result.get("agentId"), "登录应返回agentId"
        assert result.get("agentName"), "登录应返回agentName"

        # 将关键信息附加到Allure报告
        allure.attach(
            f"userToken: {result['userToken']}\n"
            f"agentId: {result['agentId']}\n"
            f"agentName: {result['agentName']}",
            name="登录返回信息",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("密码登录")
    @allure.title("逆向-使用错误密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self):
        """验证使用错误密码登录时，接口应返回失败"""
        login_api = LoginApi()
        result = login_api.login(account=LOGIN_ACCOUNT, password="wrong_password_123")

        # 错误密码应该登录失败，返回None
        assert result is None, "错误密码登录应返回None"

    @allure.story("密码登录")
    @allure.title("逆向-使用不存在的账号登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_nonexistent_account(self):
        """验证使用不存在的账号登录时，接口应返回失败"""
        login_api = LoginApi()
        result = login_api.login(account="999999999", password="any_password")

        assert result is None, "不存在的账号登录应返回None"

    @allure.story("密码登录")
    @allure.title("逆向-使用空账号登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_account(self):
        """验证使用空账号登录时，接口应返回失败"""
        login_api = LoginApi()
        result = login_api.login(account="", password=LOGIN_PASSWORD)

        assert result is None, "空账号登录应返回None"

    @allure.story("密码登录")
    @allure.title("逆向-使用空密码登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_password(self):
        """验证使用空密码登录时，接口应返回失败"""
        login_api = LoginApi()
        result = login_api.login(account=LOGIN_ACCOUNT, password="")

        assert result is None, "空密码登录应返回None"
