import pytest
import app as flask_module

@pytest.mark.buttons
def test_post_pull_data_success(client, monkeypatch):
    """测试 POST /pull_data 正常触发返回 302 重定向并可跟随到 200"""
    monkeypatch.setattr(flask_module, "is_scraping", False)
    response = client.post("/pull_data", follow_redirects=True)
    assert response.status_code == 200

@pytest.mark.buttons
def test_post_update_analysis_success(client, monkeypatch):
    """测试非 Busy 状态下 POST /update_analysis 返回 200"""
    monkeypatch.setattr(flask_module, "is_scraping", False)
    response = client.post("/update_analysis", follow_redirects=True)
    assert response.status_code == 200

@pytest.mark.buttons
def test_busy_gating_status_409(client, monkeypatch):
    """测试当系统处于 Busy 状态 (is_scraping=True) 时，POST 请求返回 409"""
    monkeypatch.setattr(flask_module, "is_scraping", True)

    # 当 is_scraping 为 True 时，update_analysis 应返回 409
    res_update = client.post("/update_analysis")
    assert res_update.status_code == 409

    # 当 is_scraping 为 True 时，pull_data 也应返回 409
    res_pull = client.post("/pull_data")
    assert res_pull.status_code == 409
