# ============================================================
# 文件说明：用户信息相关接口封装
# 作用：封装获取用户信息、余额查询等接口
# ============================================================

import allure
from utils.request_util import RequestUtil
from utils.log_util import logger


class UserApi:
    """用户信息接口封装类"""

    # 接口路径
    USER_INFO_PATH = "/ydj-web/channel/v1.0/getChannelUserByUserId"
    BALANCE_PATH = "/ydj-web/fund/balance/query/queryBalanceInfo"

    def __init__(self, token):
        """
        参数:
            token: 登录后获取的userToken
        """
        self.client = RequestUtil(token=token)

    @allure.step("获取当前登录用户信息")
    def get_user_info(self):
        """
        获取当前登录用户的详细信息。

        返回:
            Response对象
        """
        logger.info("获取用户信息...")
        return self.client.get(self.USER_INFO_PATH)

    @allure.step("查询账户余额")
    def get_balance(self):
        """
        查询当前账户的余额信息。

        返回:
            Response对象
        """
        logger.info("查询账户余额...")
        return self.client.get(self.BALANCE_PATH)
