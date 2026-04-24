# ============================================================
# 文件说明：HTTP请求封装类
# 作用：统一处理GET/POST请求、自动携带认证头、日志打印、异常捕获
# ============================================================

import json
import allure
import requests
from config.settings import BASE_URL, COMMON_HEADERS, REQUEST_TIMEOUT
from utils.log_util import logger


class RequestUtil:
    """HTTP请求工具类，封装所有接口请求的公共逻辑"""

    def __init__(self, token=None):
        """
        初始化请求工具。

        参数:
            token: 登录后获取的userToken（即请求头中的ut字段）
        """
        self.base_url = BASE_URL
        self.session = requests.Session()

        # 设置公共请求头
        self.session.headers.update(COMMON_HEADERS)

        # 如果传入了token，添加到请求头的ut字段
        if token:
            self.session.headers.update({"ut": token})

    def _build_url(self, path):
        """拼接完整的请求URL"""
        if path.startswith("http"):
            return path
        return f"{self.base_url}{path}"

    @allure.step("发送GET请求: {path}")
    def get(self, path, params=None, **kwargs):
        """
        发送GET请求。

        参数:
            path: 接口路径，如 /ydj-web/channel/v1.0/getChannelUserByUserId
            params: URL查询参数（字典）
        返回:
            Response对象
        """
        url = self._build_url(path)
        logger.info(f"[GET] {url}")
        if params:
            logger.info(f"[Params] {json.dumps(params, ensure_ascii=False)}")

        try:
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT, **kwargs)
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"[请求异常] {e}")
            raise

    @allure.step("发送POST请求: {path}")
    def post(self, path, json_data=None, data=None, **kwargs):
        """
        发送POST请求。

        参数:
            path: 接口路径
            json_data: JSON格式的请求体（字典）
            data: 表单格式的请求体
        返回:
            Response对象
        """
        url = self._build_url(path)
        logger.info(f"[POST] {url}")
        if json_data:
            logger.info(f"[Body] {json.dumps(json_data, ensure_ascii=False)}")

        try:
            response = self.session.post(
                url, json=json_data, data=data, timeout=REQUEST_TIMEOUT, **kwargs
            )
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"[请求异常] {e}")
            raise

    def _log_response(self, response):
        """记录响应日志"""
        logger.info(f"[状态码] {response.status_code}")
        try:
            body = response.json()
            # 只打印前500个字符，避免日志过长
            body_str = json.dumps(body, ensure_ascii=False)
            if len(body_str) > 500:
                body_str = body_str[:500] + "...(truncated)"
            logger.debug(f"[响应体] {body_str}")
        except Exception:
            logger.debug(f"[响应体] {response.text[:500]}")
