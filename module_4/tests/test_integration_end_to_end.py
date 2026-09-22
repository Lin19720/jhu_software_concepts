import pytest
import app as flask_module

@pytest.mark.integration
def test_end_to_end_flow(client, monkeypatch):
    """测试完整端到端流程：Pull Data -> Update Analysis -> Render Analysis Page"""
    # 1. 确保非忙碌并触发 Pull Data
    monkeypatch.setattr(flask_module, "is_scraping", False)
    res_pull = client.post("/pull_data", follow_redirects=True)
    assert res_pull.status_code == 200

    # 2. 再次重置忙碌状态，模拟后台任务结束，然后触发 Update Analysis
    monkeypatch.setattr(flask_module, "is_scraping", False)
    res_update = client.post("/update_analysis", follow_redirects=True)
    assert res_update.status_code == 200

    # 3. GET / (分析页面) 检查渲染结果
    res_page = client.get("/")
    assert res_page.status_code == 200
    html = res_page.get_data(as_text=True)
    assert "Answer:" in html
    assert "Pull Data" in html
    assert "Update Analysis" in html

@pytest.mark.integration
def test_multiple_pulls_consistency(client, monkeypatch):
    """测试多次 Pull 重叠数据时，系统与页面渲染保持一致"""
    monkeypatch.setattr(flask_module, "is_scraping", False)
    res1 = client.post("/pull_data", follow_redirects=True)
    assert res1.status_code == 200

    monkeypatch.setattr(flask_module, "is_scraping", False)
    res2 = client.post("/pull_data", follow_redirects=True)
    assert res2.status_code == 200

    res_page = client.get("/")
    assert res_page.status_code == 200
    html = res_page.get_data(as_text=True)
    assert "Answer:" in html
