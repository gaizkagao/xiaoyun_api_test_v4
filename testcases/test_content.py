# ============================================================
# 文件说明：内容接口测试用例
# 作用：验证通知公告、Banner、查价历史等接口
# ============================================================

import allure
import pytest
from api.content_api import ContentApi


@allure.epic("小云云地接")
@allure.feature("内容模块")
class TestContent:
    """内容接口测试类"""

    @allure.story("通知公告")
    @allure.title("正向-获取通知公告列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_notifications(self, login_token):
        """验证可以正确获取通知公告列表"""
        content_api = ContentApi(token=login_token)
        response = content_api.get_notifications()

        assert response.status_code == 200, f"HTTP状态码应为200，实际: {response.status_code}"

        result = response.json()
        assert result.get("status") == 200, f"业务状态码应为200，实际: {result.get('status')}"
        assert result.get("success") is True

        data = result.get("data", {})
        assert "notificationDtoList" in data, "应返回notificationDtoList字段"

        notification_list = data["notificationDtoList"]
        assert isinstance(notification_list, list), "notificationDtoList应为列表类型"

        # 验证通知公告数据结构
        if len(notification_list) > 0:
            first_group = notification_list[0]
            assert "groupName" in first_group, "应包含groupName字段"
            assert "notificationList" in first_group, "应包含notificationList字段"

            # 验证具体通知条目
            if len(first_group["notificationList"]) > 0:
                first_notification = first_group["notificationList"][0]
                assert "title" in first_notification, "通知应包含title字段"
                assert "link" in first_notification, "通知应包含link字段"

            # 附加通知列表到报告
            titles = []
            for group in notification_list:
                for n in group.get("notificationList", []):
                    titles.append(f"[{group['groupName']}] {n.get('title', '无标题')}")
            allure.attach(
                "\n".join(titles[:10]),
                name="通知公告列表（前10条）",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Banner管理")
    @allure.title("正向-获取Banner配置列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_banner_list(self, login_token):
        """验证可以正确获取Banner配置列表"""
        content_api = ContentApi(token=login_token)
        response = content_api.get_banner_list()

        assert response.status_code == 200

        result = response.json()
        assert result.get("status") == 200
        assert result.get("success") is True

        data = result.get("data", {})
        assert "list" in data, "应返回list字段"
        assert isinstance(data["list"], list), "list应为列表类型"

        # 验证Banner数据结构
        if len(data["list"]) > 0:
            first_banner = data["list"][0]
            assert "bannerUrl" in first_banner, "Banner应包含bannerUrl字段"
            assert "keywordGroup" in first_banner, "Banner应包含keywordGroup字段"

        # 附加分页信息
        allure.attach(
            f"总数: {data.get('total', 0)}\n"
            f"当前页: {data.get('pageNo', 0)}\n"
            f"每页数量: {data.get('pageSize', 0)}\n"
            f"总页数: {data.get('totalPages', 0)}",
            name="Banner分页信息",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("查价历史")
    @allure.title("正向-获取包车查价历史记录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_quote_history(self, login_token):
        """验证可以正确获取包车查价历史记录"""
        content_api = ContentApi(token=login_token)
        response = content_api.get_quote_history(quote_type="CAR")

        assert response.status_code == 200

        result = response.json()
        assert result.get("status") == 200
        assert result.get("success") is True

        data = result.get("data")
        assert data is not None, "data不应为None"
        assert isinstance(data, list), "data应为列表类型"

        # 验证查价历史数据结构
        if len(data) > 0:
            first_record = data[0]
            assert "quoteType" in first_record, "应包含quoteType字段"
            assert "tripName" in first_record, "应包含tripName字段"
            assert first_record["quoteType"] == "CAR", "查价类型应为CAR"

            # 附加查价历史到报告
            history_lines = []
            for record in data[:5]:
                history_lines.append(
                    f"{record.get('tripName', '未知')} "
                    f"({record.get('startDate', '')} ~ {record.get('endDate', '')})"
                )
            allure.attach(
                "\n".join(history_lines),
                name="查价历史（前5条）",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Banner管理")
    @allure.title("边界-使用不存在的分组查询Banner")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_banner_nonexistent_group(self, login_token):
        """验证查询不存在的Banner分组时，接口应返回空列表"""
        content_api = ContentApi(token=login_token)
        response = content_api.get_banner_list(keyword_group="不存在的分组_test_xyz")

        assert response.status_code == 200

        result = response.json()
        assert result.get("status") == 200

        data = result.get("data", {})
        assert data.get("total", 0) == 0 or len(data.get("list", [])) == 0, \
            "不存在的分组应返回空结果"
