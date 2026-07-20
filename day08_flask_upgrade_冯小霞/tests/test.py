import pytest
from app import app  # 替换成你项目主文件名

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# 测试1：健康接口 /health 返回200
def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200

# 测试2：未登录访问 /api/metrics 被拦截（无登录session）
def test_metrics_unlogin_blocked(client):
    resp = client.get("/api/metrics")
    # 未登录跳转/403，不会正常返回200
    assert resp.status_code != 200

# 测试3：登录后访问 /api/metrics 返回ok与metrics字段
def test_metrics_login_success(client):
    # 模拟登录，写入session
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    resp = client.get("/api/metrics")
    data = resp.get_json()
    assert resp.status_code == 200
    assert "ok" in data
    assert data["ok"] is True
    assert "metrics" in data
    assert isinstance(data["metrics"], list)

# 测试4：带分类参数 /api/categories?category=Fashion 返回筛选结果
def test_categories_filter_fashion(client):
    # 先登录
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    resp = client.get("/api/categories?category=Fashion")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["category"] == "Fashion"
    assert "rows" in data
    # 校验是筛选后的列表
    assert isinstance(data["rows"], list)