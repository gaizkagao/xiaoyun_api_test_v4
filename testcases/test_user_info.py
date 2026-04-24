# ============================================================
# 文件说明：用户信息接口测试用例
# 作用：验证获取用户信息、查询余额等接口
# ============================================================

import allure
import pytest
from api.user_api import UserApi


@allure.epic("小云云地接")
@allure.feature("用户信息模块")
class TestUserInfo:
    """用户信息接口测试类"""

    @allure.story("获取用户信息")
    @allure.title("正向-获取当前登录用户的详细信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_info_success(self, login_token):
        """验证登录后可以正确获取用户详细信息"""
        user_api = UserApi(token=login_token)
        response = user_api.get_user_info()

        # 断言HTTP状态码
        assert response.status_code == 200, f"HTTP状态码应为200，实际: {response.status_code}"

        result = response.json()

        # 断言业务状态码
        assert result.get("status") == 200, f"业务状态码应为200，实际: {result.get('status')}"
        assert result.get("success") is True, "success字段应为True"

        # 断言返回了必要的用户信息字段
        data = result.get("data", {})
        assert data.get("loginName"), "应返回loginName"
        assert data.get("realName"), "应返回realName"
        assert data.get("userId"), "应返回userId"
        assert data.get("agentId"), "应返回agentId"
        assert data.get("mobile"), "应返回mobile"

        # 验证返回的登录名与配置一致
        assert data["loginName"] == "gaozheng_test", \
            f"loginName应为131888，实际: {data['loginName']}"

        # 附加用户信息到报告
        allure.attach(
            f"登录名: {data.get('loginName')}\n"
            f"真实姓名: {data.get('realName')}\n"
            f"手机号: {data.get('mobile')}\n"
            f"用户ID: {data.get('userId')}\n"
            f"商户ID: {data.get('agentId')}",
            name="用户详细信息",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("查询余额")
    @allure.title("正向-查询当前账户余额信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_balance_success(self, login_token):
        """验证登录后可以正确查询账户余额"""
        user_api = UserApi(token=login_token)
        response = user_api.get_balance()

        assert response.status_code == 200, f"HTTP状态码应为200，实际: {response.status_code}"

        result = response.json()
        assert result.get("status") == 200, f"业务状态码应为200，实际: {result.get('status')}"
        assert result.get("success") is True, "success字段应为True"

        # 验证余额数据结构
        data = result.get("data", {})
        assert data.get("rtCode") == 200, f"rtCode应为200，实际: {data.get('rtCode')}"
        assert data.get("rtData") is not None, "rtData不应为None"
        assert isinstance(data["rtData"], list), "rtData应为列表类型"
        assert len(data["rtData"]) > 0, "rtData不应为空列表"

        # 验证余额数据字段
        first_account = data["rtData"][0]
        assert "amount" in first_account, "余额数据应包含amount字段"
        assert "accountName" in first_account, "余额数据应包含accountName字段"
        assert first_account["amount"] >= 0, "余额不应为负数"

        # 附加余额信息到报告（金额单位为分，转换为元显示）
        for acc in data["rtData"]:
            allure.attach(
                f"账户名: {acc.get('accountName')}\n"
                f"余额: ￥{acc.get('amount', 0) / 100:.2f}\n"
                f"账户类型: {acc.get('accountType')}\n"
                f"冻结金额: ￥{acc.get('frozenAmount', 0) / 100:.2f}",
                name=f"账户-{acc.get('accountName')}-类型{acc.get('accountType')}",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("获取用户信息")
    @allure.title("逆向-使用无效Token获取用户信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_user_info_invalid_token(self):
        """验证使用无效Token时，接口应返回认证失败"""
        user_api = UserApi(token="invalid_token_12345")
        response = user_api.get_user_info()

        result = response.json()
        # 无效Token应返回非200的业务状态码（如10012会话过期）
        assert (
            response.status_code != 200
            or result.get("status") != 200
            or result.get("success") is not True
        ), "无效Token不应成功获取用户信息"

        # 附加错误信息到报告
        allure.attach(
            f"HTTP状态码: {response.status_code}\n"
            f"业务状态码: {result.get('status')}\n"
            f"错误信息: {result.get('message')}",
            name="无效Token响应",
            attachment_type=allure.attachment_type.TEXT
        )
