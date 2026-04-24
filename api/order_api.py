# ============================================================
# 文件说明：订单相关接口封装
# 作用：封装订单列表、订单状态统计、订单数量等接口
# ============================================================

import allure
from utils.request_util import RequestUtil
from utils.log_util import logger


class OrderApi:
    """订单接口封装类"""

    # 接口路径
    ORDER_COUNT_PATH = "/ydj-web/orderTravel/ydj/v5.0/getTravelOrderCountForYdjV5"
    ORDER_STATUS_NUM_PATH = "/ydj-web/orderTravel/ydj/v5.0/getTravelOrderStatusNumForYdjAll"
    ORDER_LIST_PATH = "/ydj-web/orderTravel/ydj/v5.0/getTravelOrderListForYdjAll"

    def __init__(self, token):
        """
        参数:
            token: 登录后获取的userToken
        """
        self.client = RequestUtil(token=token)

    @allure.step("查询各类型订单数量统计")
    def get_order_count(self):
        """
        查询各业务类型（包车/接送机/定制游）的订单数量统计。

        返回:
            Response对象
        """
        logger.info("查询各类型订单数量统计...")
        return self.client.post(self.ORDER_COUNT_PATH, json_data={})

    @allure.step("查询订单状态数量分布")
    def get_order_status_num(self, order_type=""):
        """
        查询订单按状态分类的数量分布。

        参数:
            order_type: 订单类型筛选，空字符串表示全部
        返回:
            Response对象
        """
        logger.info(f"查询订单状态数量，订单类型: {order_type or '全部'}")
        return self.client.post(
            self.ORDER_STATUS_NUM_PATH,
            json_data={"orderType": order_type}
        )

    @allure.step("查询订单列表")
    def get_order_list(self, offset=0, limit=10, order_type="",
                       order_travel_status="", customer_name="",
                       customer_mobile="", order_travel_no="",
                       travel_no="", travel_group_number="",
                       create_time_start="", create_time_end=""):
        """
        查询订单列表（支持多条件筛选和分页）。

        参数:
            offset: 分页偏移量（从0开始）
            limit: 每页数量（默认10）
            order_type: 订单类型筛选
            order_travel_status: 订单状态筛选
            customer_name: 联系人姓名筛选
            customer_mobile: 联系电话筛选
            order_travel_no: 订单编号筛选
            travel_no: 行程单号筛选
            travel_group_number: 内部团号筛选
            create_time_start: 下单开始时间
            create_time_end: 下单结束时间
        返回:
            Response对象
        """
        request_body = {
            "offset": offset,
            "limit": limit,
            "orderType": order_type,
            "orderTravelStatus": order_travel_status,
            "customerName": customer_name,
            "customerMobile": customer_mobile,
            "orderTravelNo": order_travel_no,
            "travelNo": travel_no,
            "travelGroupNumber": travel_group_number,
            "createTimeStart": create_time_start,
            "createTimeEnd": create_time_end,
        }
        logger.info(f"查询订单列表，offset={offset}, limit={limit}")
        return self.client.post(self.ORDER_LIST_PATH, json_data=request_body)
