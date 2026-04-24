# ============================================================
# 文件说明：登录接口封装
# 作用：封装小云云地接的登录接口，返回认证Token
# ============================================================

import allure
from utils.request_util import RequestUtil
from utils.log_util import logger


class LoginApi:
    """登录接口封装类"""

    # 登录接口路径
    LOGIN_PATH = "/ydj-web/login/v1.0/passwordLogin"

    def __init__(self):
        # 登录接口不需要Token，所以不传token参数
        self.client = RequestUtil()

    @allure.step("调用登录接口，账号: {account}")
    def login(self, account, password):
        """
        调用密码登录接口。

        参数:
            account: 登录账号（如 gaozheng_test）
            password: 登录密码

        返回:
            dict: 包含 userToken 和完整登录响应的字典
                  {"userToken": "xxx", "response": {...}}
            None: 登录失败时返回None
        """
        request_body = {
            "userType": "d",
            "loginName": account,
            "password": password
        }

        logger.info(f"正在登录，账号: {account}")
        response = self.client.post(self.LOGIN_PATH, json_data=request_body)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == 200 and result.get("data"):
                user_token = result["data"].get("userToken")
                if user_token:
                    logger.info(f"登录成功！userToken: {user_token}")
                    return {
                        "userToken": user_token,
                        "userId": result["data"].get("userId"),
                        "agentId": result["data"].get("agentId"),
                        "agentName": result["data"].get("agentName"),
                        "realName": result["data"].get("realName"),
                        "response": result
                    }

        logger.error(f"登录失败！响应: {response.text[:500]}")
        return None
