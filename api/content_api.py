# ============================================================
# 文件说明：内容相关接口封装
# 作用：封装通知公告、Banner等内容类接口
# ============================================================

import allure
from utils.request_util import RequestUtil
from utils.log_util import logger


class ContentApi:
    """内容接口封装类（通知公告、Banner等）"""

    # 接口路径
    NOTIFICATION_PATH = "/ydj-web/quote/v1.0/getHbcNotification/List"
    BANNER_PATH = "/ydj-web/quote/p/v1.0/hbcConfigBanner/list"
    QUOTE_HISTORY_PATH = "/ydj-web/businessTrip/c/v1.0/queryQuoteHistory"

    def __init__(self, token):
        """
        参数:
            token: 登录后获取的userToken
        """
        self.client = RequestUtil(token=token)

    @allure.step("获取通知公告列表")
    def get_notifications(self, version="1.0.0"):
        """
        获取通知公告列表。

        参数:
            version: 版本号，默认1.0.0
        返回:
            Response对象
        """
        logger.info("获取通知公告列表...")
        return self.client.get(
            self.NOTIFICATION_PATH,
            params={"version": version}
        )

    @allure.step("获取Banner列表")
    def get_banner_list(self, keyword_group="小云底部图片", page_no=0, page_size=100):
        """
        获取Banner配置列表。

        参数:
            keyword_group: Banner分组关键词
            page_no: 页码
            page_size: 每页数量
        返回:
            Response对象
        """
        logger.info(f"获取Banner列表，分组: {keyword_group}")
        return self.client.post(
            self.BANNER_PATH,
            json_data={
                "keywordGroup": keyword_group,
                "pageNo": page_no,
                "pageSize": page_size
            }
        )

    @allure.step("获取查价历史记录")
    def get_quote_history(self, quote_type="CAR"):
        """
        获取查价历史记录。

        参数:
            quote_type: 查价类型，默认CAR（包车）
        返回:
            Response对象
        """
        logger.info(f"获取查价历史，类型: {quote_type}")
        return self.client.get(
            self.QUOTE_HISTORY_PATH,
            params={"quoteType": quote_type}
        )
