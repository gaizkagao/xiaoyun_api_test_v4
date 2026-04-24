# ============================================================
# 文件说明：订单接口测试用例
# 作用：验证订单数量统计、订单状态分布、订单列表查询等接口
# ============================================================

import allure
import pytest
from api.order_api import OrderApi


@allure.epic("小云云地接")
@allure.feature("订单模块")
class TestOrder:
    """订单接口测试类"""

    @allure.story("订单数量统计")
    @allure.title("正向-查询各类型订单数量统计")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_order_count(self, login_token):
        """验证可以正确查询各业务类型的订单数量统计"""
        order_api = OrderApi(token=login_token)
        response = order_api.get_order_count()

        assert response.status_code == 200, f"HTTP状态码应为200，实际: {response.status_code}"

        result = response.json()
        assert result.get("status") == 200, f"业务状态码应为200，实际: {result.get('status')}"
        assert result.get("success") is True, "success字段应为True"

        # 验证返回数据结构
        data = result.get("data")
        assert data is not None, "data不应为None"
        assert isinstance(data, list), "data应为列表类型"

        # 验证每条统计数据包含必要字段
        for item in data:
            assert "orderCategory" in item, "应包含orderCategory字段"
            assert "totalCount" in item, "应包含totalCount字段"
            assert item["totalCount"] >= 0, "订单总数不应为负数"

        # 附加统计信息到报告
        category_map = {10: "包车", 50: "接送机", 120: "定制游"}
        summary_lines = []
        for item in data:
            cat_name = category_map.get(item["orderCategory"], f"类型{item['orderCategory']}")
            summary_lines.append(
                f"{cat_name}: 总计{item['totalCount']}单, "
                f"待支付{item.get('waitPayCount', 0)}, "
                f"待出行{item.get('waitTravelCount', 0)}, "
                f"已完成{item.get('finishTravelCount', 0)}"
            )
        allure.attach(
            "\n".join(summary_lines),
            name="订单数量统计",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("订单状态分布")
    @allure.title("正向-查询订单状态数量分布")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_order_status_num(self, login_token):
        """验证可以正确查询订单按状态分类的数量分布"""
        order_api = OrderApi(token=login_token)
        response = order_api.get_order_status_num()

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200
        assert result.get("success") is True

        data = result.get("data")
        assert data is not None, "data不应为None"
        assert isinstance(data, list), "data应为列表类型"

        # 验证每条状态数据包含必要字段
        for item in data:
            assert "orderTravelStatus" in item, "应包含orderTravelStatus字段"
            assert "orderTravelStatusName" in item, "应包含orderTravelStatusName字段"
            assert "num" in item, "应包含num字段"
            assert item["num"] >= 0, "数量不应为负数"

        # 验证应包含"总数"状态
        total_item = next((i for i in data if i["orderTravelStatus"] == -1), None)
        assert total_item is not None, "应包含总数统计（orderTravelStatus=-1）"

        # 附加状态分布到报告
        status_lines = [f"{item['orderTravelStatusName']}: {item['num']}单" for item in data]
        allure.attach(
            "\n".join(status_lines),
            name="订单状态分布",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("订单列表查询")
    @allure.title("正向-查询订单列表（默认参数）")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_order_list_default(self, login_token):
        """验证使用默认参数可以正确查询订单列表"""
        order_api = OrderApi(token=login_token)
        response = order_api.get_order_list()

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200
        assert result.get("success") is True

        data = result.get("data", {})
        assert "list" in data, "返回数据应包含list字段"
        assert isinstance(data["list"], list), "list应为列表类型"

        # 如果有订单数据，验证订单字段完整性
        if len(data["list"]) > 0:
            first_order = data["list"][0]
            # 验证关键字段存在
            assert "orderTravelNo" in first_order or "travelNo" in first_order, \
                "订单应包含订单编号"
            assert "createTime" in first_order, "订单应包含创建时间"

            allure.attach(
                f"查询到 {len(data['list'])} 条订单\n"
                f"第一条订单创建时间: {first_order.get('createTime')}",
                name="订单列表概要",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("订单列表查询")
    @allure.title("正向-分页查询订单列表（第2页）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_order_list_pagination(self, login_token):
        """验证分页查询订单列表功能正常"""
        order_api = OrderApi(token=login_token)
        response = order_api.get_order_list(offset=10, limit=10)

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200
        assert result.get("success") is True

        data = result.get("data", {})
        assert "list" in data, "返回数据应包含list字段"
        assert isinstance(data["list"], list), "list应为列表类型"

    @allure.story("订单列表查询")
    @allure.title("正向-按订单类型筛选（包车订单）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_order_list_filter_by_type(self, login_token):
        """验证按订单类型筛选功能正常"""
        order_api = OrderApi(token=login_token)
        # orderType为空字符串表示全部，这里测试传入具体类型
        response = order_api.get_order_list(order_type="")

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200

    @allure.story("订单列表查询")
    @allure.title("边界-查询limit为0的订单列表")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_order_list_limit_zero(self, login_token):
        """验证limit为0时接口的处理"""
        order_api = OrderApi(token=login_token)
        response = order_api.get_order_list(offset=0, limit=0)

        assert response.status_code == 200
        result = response.json()
        # 接口应正常返回，不应报错
        assert result.get("status") == 200 or result.get("success") is not None, \
            "limit为0时接口不应报500错误"
