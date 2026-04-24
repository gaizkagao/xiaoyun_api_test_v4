# ============================================================
# 文件说明：全局配置文件
# 作用：集中管理所有环境地址、账号信息、公共参数
# ============================================================

# ---------- 环境配置 ----------
# 小云云地接API网关地址
BASE_URL = "https://api-gw.huangbaoche.com"

# ---------- 登录账号 ----------
LOGIN_ACCOUNT = "gaozheng_test"
LOGIN_PASSWORD = "gz260203"

# ---------- 公共请求头（固定值）----------
# X-CCLX-Api-Key 和 ak 是系统级固定参数，所有接口都需要携带
COMMON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "X-CCLX-Api-Key": "68c92f69-053d-4d83-bf79-00532652e0ad",
    "ak": "123123",
}

# ---------- 超时设置 ----------
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
