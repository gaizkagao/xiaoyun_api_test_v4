# ============================================================
# 文件说明：线索行程列表查询接口封装
# 作用：封装 /ydj-web/clue/v1.0/queryClueTripList 接口
# 业务说明：该接口用于查询线索下的行程列表，支持多条件筛选和分页
# ============================================================

import allure
from utils.request_util import RequestUtil
from utils.log_util import logger


class QueryClueTripListApi:
    """线索相关接口封装类"""

    # 接口路径
    CLUE_TRIP_LIST_PATH = "/ydj-web/clue/v1.0/queryClueTripList"

    def __init__(self, token):
        """
        初始化线索接口。

        参数:
            token: 登录后获取的userToken
        """
        self.client = RequestUtil(token=token)

    @allure.step("查询线索行程列表")
    def query_clue_trip_list(self, limit=10, offset=1, create_by_name="",
                              clue_no="", clue_status=None, user_id="",
                              user_name="", channel_hover=False,
                              clue_status_hover=False,
                              handled_resource_types=None,
                              clue_name="", from_source=1):
        """
        查询线索行程列表（支持多条件筛选和分页）。

        参数:
            limit: 每页数量（默认10）
            offset: 分页页码（从1开始，1=第一页，2=第二页）
            create_by_name: 创建人姓名筛选
            clue_no: 线索编号筛选
            clue_status: 线索状态筛选（None表示全部）
            user_id: 用户ID筛选
            user_name: 用户姓名筛选
            channel_hover: 渠道悬浮标记
            clue_status_hover: 线索状态悬浮标记
            handled_resource_types: 已处理资源类型列表
            clue_name: 线索名称筛选
            from_source: 来源（1=默认）
        返回:
            Response对象
        """
        if handled_resource_types is None:
            handled_resource_types = []

        request_body = {
            "limit": limit,
            "offset": offset,
            "createByName": create_by_name,
            "clueNo": clue_no,
            "clueStatus": clue_status,
            "userId": user_id,
            "userName": user_name,
            "channelHover": channel_hover,
            "clueStatusHover": clue_status_hover,
            "handledResourceTypes": handled_resource_types,
            "clueName": clue_name,
            "from": from_source,
        }
        logger.info(f"查询线索行程列表，limit={limit}, offset={offset}, "
                     f"clueNo={clue_no or '无'}, clueStatus={clue_status}")
        return self.client.post(self.CLUE_TRIP_LIST_PATH, json_data=request_body)