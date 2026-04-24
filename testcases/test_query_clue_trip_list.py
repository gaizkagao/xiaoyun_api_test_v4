# ============================================================
# 文件说明：线索行程列表查询接口测试用例
# 接口路径：/ydj-web/clue/v1.0/queryClueTripList
# 覆盖范围：正向查询（默认/分页/筛选）+ 逆向测试（异常参数/无效Token）
# 重要说明：该接口的offset字段是页码（从1开始），不是偏移量
# ============================================================

import pytest
import allure
from api.query_clue_trip_list_api import QueryClueTripListApi
from utils.log_util import logger


@allure.epic("小云云地接")
@allure.feature("线索管理")
class TestClueTripList:
    """线索行程列表查询接口测试"""

    # ==================== 正向测试 ====================

    @allure.story("默认查询")
    @allure.title("默认参数查询线索行程列表")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_query_default(self, login_token):
        """
        测试场景：使用默认参数查询线索行程列表（offset=1, limit=10）
        预期结果：返回成功，包含list列表和total总数
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list()

        # 第一层断言：HTTP状态码
        assert response.status_code == 200, f"HTTP状态码异常: {response.status_code}"

        result = response.json()

        # 第二层断言：业务状态码
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"
        assert result.get("success") is True, f"success字段异常: {result.get('success')}"

        # 第三层断言：业务数据结构
        data = result.get("data")
        assert data is not None, "data字段为空"
        assert "list" in data, "data中缺少list字段"
        assert "total" in data, "data中缺少total字段"
        assert "size" in data, "data中缺少size字段"
        assert isinstance(data["list"], list), "list字段不是数组类型"
        assert data["total"] >= 0, "total不应为负数"
        assert data["size"] == 10, f"size应为默认值10，实际: {data['size']}"

        allure.attach(
            f"总记录数: {data['total']}\n返回条数: {len(data['list'])}\nsize: {data['size']}",
            name="查询结果摘要",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("默认查询")
    @allure.title("验证线索列表数据字段完整性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_clue_data_fields(self, login_token):
        """
        测试场景：验证返回的线索数据包含所有必要字段
        预期结果：每条线索记录包含clueNo、channelName、status、createByName等核心字段
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list()
        result = response.json()
        data = result.get("data", {})
        clue_list = data.get("list", [])

        # 如果列表不为空，验证第一条数据的字段完整性
        if len(clue_list) > 0:
            first_clue = clue_list[0]

            # 必须存在的核心字段
            required_fields = [
                "clueNo",           # 线索编号
                "channelName",      # 渠道名称
                "merchantName",     # 商户名称
                "status",           # 线索状态
                "createByName",     # 创建人
                "createTime",       # 创建时间
                "clueCreateTime",   # 线索创建时间
                "followerName",     # 跟进人
                "contactPerson",    # 联系人
                "travellerRspList", # 出行人列表
                "tripOrderList",    # 行程订单列表
            ]

            missing_fields = [f for f in required_fields if f not in first_clue]
            assert len(missing_fields) == 0, f"缺少必要字段: {missing_fields}"

            # 验证线索编号格式（以CL开头）
            assert first_clue["clueNo"].startswith("CL"), \
                f"线索编号格式异常，应以CL开头: {first_clue['clueNo']}"

            # 验证行程订单列表是数组类型
            assert isinstance(first_clue["tripOrderList"], list), \
                "tripOrderList应为数组类型"

            allure.attach(
                f"线索编号: {first_clue['clueNo']}\n"
                f"渠道: {first_clue['channelName']}\n"
                f"状态: {first_clue['status']}\n"
                f"创建人: {first_clue['createByName']}\n"
                f"行程订单数: {len(first_clue['tripOrderList'])}",
                name="首条线索数据摘要",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            allure.attach("线索列表为空，跳过字段验证", name="说明",
                          attachment_type=allure.attachment_type.TEXT)

    @allure.story("默认查询")
    @allure.title("验证行程订单数据字段完整性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_trip_order_fields(self, login_token):
        """
        测试场景：验证线索下的行程订单数据包含必要字段
        预期结果：含有订单的行程记录应包含tripNo、tripName、tripStatus等字段
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list()
        result = response.json()
        clue_list = result.get("data", {}).get("list", [])

        # 找到第一条包含行程订单的线索
        clue_with_orders = None
        for clue in clue_list:
            if clue.get("tripOrderList") and len(clue["tripOrderList"]) > 0:
                clue_with_orders = clue
                break

        if clue_with_orders:
            first_order = clue_with_orders["tripOrderList"][0]

            # 行程订单必须存在的字段
            required_order_fields = [
                "tripNo",       # 行程单号
                "tripName",     # 行程名称
                "tripStatus",   # 行程状态
                "updateTime",   # 更新时间
            ]

            missing = [f for f in required_order_fields if f not in first_order]
            assert len(missing) == 0, f"行程订单缺少必要字段: {missing}"

            # 验证行程单号格式（以TP开头）
            assert first_order["tripNo"].startswith("TP"), \
                f"行程单号格式异常，应以TP开头: {first_order['tripNo']}"

            allure.attach(
                f"线索编号: {clue_with_orders['clueNo']}\n"
                f"行程单号: {first_order['tripNo']}\n"
                f"行程名称: {first_order['tripName']}\n"
                f"行程状态: {first_order['tripStatus']}",
                name="行程订单数据摘要",
                attachment_type=allure.attachment_type.TEXT
            )
        else:
            allure.attach("未找到包含行程订单的线索，跳过验证", name="说明",
                          attachment_type=allure.attachment_type.TEXT)

    # ==================== 分页测试 ====================

    @allure.story("分页查询")
    @allure.title("自定义每页数量查询（limit=5）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_query_custom_limit(self, login_token):
        """
        测试场景：设置limit=5查询线索列表
        预期结果：返回的list长度不超过5，size=5
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list(limit=5, offset=1)

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"
        assert result.get("success") is True

        data = result.get("data", {})
        assert data["size"] == 5, f"size应为5，实际: {data['size']}"
        assert len(data["list"]) <= 5, f"返回条数应≤5，实际: {len(data['list'])}"

        allure.attach(
            f"请求limit: 5\n返回条数: {len(data['list'])}\nsize: {data['size']}",
            name="分页结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("分页查询")
    @allure.title("翻页查询（offset=2，第2页）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_query_pagination_offset(self, login_token):
        """
        测试场景：设置offset=2查询第2页数据
        预期结果：返回成功，且与第1页数据不同（如果总数据量足够）
        """
        clue_api = QueryClueTripListApi(token=login_token)

        # 先查第1页
        response_page1 = clue_api.query_clue_trip_list(limit=5, offset=1)
        result_page1 = response_page1.json()
        list_page1 = result_page1.get("data", {}).get("list", [])

        # 再查第2页
        response_page2 = clue_api.query_clue_trip_list(limit=5, offset=2)
        assert response_page2.status_code == 200
        result_page2 = response_page2.json()
        assert result_page2.get("status") == 200, f"业务状态码异常: {result_page2.get('status')}, message: {result_page2.get('message')}"

        list_page2 = result_page2.get("data", {}).get("list", [])

        # 如果两页都有数据，验证数据不同
        if len(list_page1) > 0 and len(list_page2) > 0:
            clue_nos_page1 = {c["clueNo"] for c in list_page1}
            clue_nos_page2 = {c["clueNo"] for c in list_page2}
            # 两页的线索编号不应完全相同
            assert clue_nos_page1 != clue_nos_page2, "第1页和第2页数据完全相同，分页可能未生效"

        allure.attach(
            f"第1页条数: {len(list_page1)}\n第2页条数: {len(list_page2)}",
            name="分页对比结果",
            attachment_type=allure.attachment_type.TEXT
        )

    # ==================== 条件筛选测试 ====================

    @allure.story("条件筛选")
    @allure.title("按线索编号精确查询")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_query_by_clue_no(self, login_token):
        """
        测试场景：通过线索编号精确查询
        预期结果：返回的结果中包含指定线索编号的记录
        """
        clue_api = QueryClueTripListApi(token=login_token)

        # 先查询默认列表，获取一个真实的线索编号
        response_default = clue_api.query_clue_trip_list()
        default_list = response_default.json().get("data", {}).get("list", [])

        if len(default_list) == 0:
            pytest.skip("线索列表为空，跳过按编号查询测试")

        target_clue_no = default_list[0]["clueNo"]

        # 用该编号进行精确查询
        response = clue_api.query_clue_trip_list(clue_no=target_clue_no)
        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"
        assert result.get("success") is True

        data = result.get("data", {})
        clue_list = data.get("list", [])

        # 验证返回结果中包含目标线索
        found = any(c["clueNo"] == target_clue_no for c in clue_list)
        assert found, f"按编号 {target_clue_no} 查询，结果中未找到该线索"

        allure.attach(
            f"查询线索编号: {target_clue_no}\n返回条数: {len(clue_list)}\n是否命中: {found}",
            name="精确查询结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("条件筛选")
    @allure.title("按创建人姓名筛选")
    @allure.severity(allure.severity_level.NORMAL)
    def test_query_by_create_by_name(self, login_token):
        """
        测试场景：按创建人姓名筛选线索
        预期结果：返回的所有线索的创建人都匹配筛选条件
        """
        clue_api = QueryClueTripListApi(token=login_token)

        # 先查询默认列表，获取一个真实的创建人姓名
        response_default = clue_api.query_clue_trip_list()
        default_list = response_default.json().get("data", {}).get("list", [])

        if len(default_list) == 0:
            pytest.skip("线索列表为空，跳过按创建人查询测试")

        target_name = default_list[0]["createByName"]

        # 用该创建人姓名进行筛选查询
        response = clue_api.query_clue_trip_list(create_by_name=target_name)
        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"

        clue_list = result.get("data", {}).get("list", [])

        # 验证返回结果中所有线索的创建人都匹配
        if len(clue_list) > 0:
            for clue in clue_list:
                assert clue["createByName"] == target_name, \
                    f"创建人不匹配: 期望 {target_name}，实际 {clue['createByName']}"

        allure.attach(
            f"筛选创建人: {target_name}\n返回条数: {len(clue_list)}",
            name="创建人筛选结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("条件筛选")
    @allure.title("按线索状态筛选（status=1 跟进中）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_query_by_clue_status(self, login_token):
        """
        测试场景：按线索状态筛选（status=1表示跟进中）
        预期结果：返回的所有线索状态都为1
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list(clue_status=1)

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"

        clue_list = result.get("data", {}).get("list", [])

        # 验证返回结果中所有线索状态都为"1"
        if len(clue_list) > 0:
            for clue in clue_list:
                assert str(clue["status"]) == "1", \
                    f"线索 {clue['clueNo']} 状态不匹配: 期望 '1'，实际 '{clue['status']}'"

        allure.attach(
            f"筛选状态: 1（跟进中）\n返回条数: {len(clue_list)}",
            name="状态筛选结果",
            attachment_type=allure.attachment_type.TEXT
        )

    # ==================== 逆向测试 ====================

    @allure.story("逆向测试")
    @allure.title("查询不存在的线索编号")
    @allure.severity(allure.severity_level.NORMAL)
    def test_query_nonexistent_clue_no(self, login_token):
        """
        测试场景：使用一个不存在的线索编号进行查询
        预期结果：返回成功但列表为空，total为0
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list(clue_no="CL9999999999999")

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"
        assert result.get("success") is True

        data = result.get("data", {})
        assert len(data.get("list", [])) == 0, "查询不存在的编号应返回空列表"
        assert data.get("total", 0) == 0, f"查询不存在的编号total应为0，实际: {data.get('total')}"

        allure.attach(
            f"查询编号: CL9999999999999\n返回条数: {len(data.get('list', []))}\ntotal: {data.get('total')}",
            name="不存在编号查询结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("逆向测试")
    @allure.title("offset=0 边界值查询（页码不能小于1）")
    @allure.severity(allure.severity_level.MINOR)
    def test_query_offset_zero(self, login_token):
        """
        测试场景：设置offset=0查询（页码从1开始，0是非法值）
        预期结果：接口应返回错误提示"分页页码不能小于1"
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list(offset=0)

        assert response.status_code == 200
        result = response.json()

        # offset=0 应该返回业务错误
        assert result.get("status") != 200 or result.get("success") is not True, \
            "offset=0应返回业务错误，但接口返回了成功"

        allure.attach(
            f"offset=0 返回状态: {result.get('status')}\n"
            f"message: {result.get('message', '无')}",
            name="边界值测试结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("逆向测试")
    @allure.title("超大offset翻页查询")
    @allure.severity(allure.severity_level.MINOR)
    def test_query_large_offset(self, login_token):
        """
        测试场景：设置一个超大的offset值（远超实际数据页数）
        预期结果：返回成功但列表为空（已超出数据范围）
        """
        clue_api = QueryClueTripListApi(token=login_token)
        response = clue_api.query_clue_trip_list(offset=99999)

        assert response.status_code == 200
        result = response.json()
        assert result.get("status") == 200, f"业务状态码异常: {result.get('status')}, message: {result.get('message')}"

        data = result.get("data", {})
        assert len(data.get("list", [])) == 0, \
            f"超大offset应返回空列表，实际返回 {len(data.get('list', []))} 条"

        allure.attach(
            f"offset=99999 返回条数: {len(data.get('list', []))}",
            name="超大offset测试结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("逆向测试")
    @allure.title("无效Token查询线索列表")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_query_with_invalid_token(self):
        """
        测试场景：使用无效的Token查询线索列表
        预期结果：接口应拒绝请求，返回认证失败相关错误
        """
        clue_api = QueryClueTripListApi(token="invalid_token_12345")
        response = clue_api.query_clue_trip_list()

        result = response.json()

        # 无效Token应该导致认证失败
        is_auth_failed = (
            response.status_code != 200
            or result.get("status") != 200
            or result.get("success") is not True
        )
        assert is_auth_failed, "使用无效Token应返回认证失败，但接口返回了成功"

        allure.attach(
            f"HTTP状态码: {response.status_code}\n"
            f"业务状态码: {result.get('status')}\n"
            f"success: {result.get('success')}\n"
            f"message: {result.get('message', '无')}",
            name="无效Token测试结果",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("逆向测试")
    @allure.title("不携带Token查询线索列表")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_query_without_token(self):
        """
        测试场景：不携带Token（未登录状态）查询线索列表
        预期结果：接口应拒绝请求，返回未登录/认证失败错误
        """
        clue_api = QueryClueTripListApi(token=None)
        response = clue_api.query_clue_trip_list()

        result = response.json()

        # 不携带Token应该导致认证失败
        is_auth_failed = (
            response.status_code != 200
            or result.get("status") != 200
            or result.get("success") is not True
        )
        assert is_auth_failed, "不携带Token应返回认证失败，但接口返回了成功"

        allure.attach(
            f"HTTP状态码: {response.status_code}\n"
            f"业务状态码: {result.get('status')}\n"
            f"success: {result.get('success')}\n"
            f"message: {result.get('message', '无')}",
            name="无Token测试结果",
            attachment_type=allure.attachment_type.TEXT
        )