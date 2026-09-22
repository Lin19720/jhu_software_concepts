import pytest

@pytest.mark.web
def test_app_factory_routes(app):
    """验证所需路由均已注册"""
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/" in rules
    assert "/pull_data" in rules
    assert "/update_analysis" in rules

@pytest.mark.web
def test_get_analysis_page(client):
    """测试 GET / (分析页面) 渲染及关键文本元素"""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # 验证页面包含两个核心按钮
    assert "Pull Data" in html
    assert "Update Analysis" in html

    # 验证页面包含要求的标签文本
    assert "Analysis" in html
    assert "Answer:" in html
