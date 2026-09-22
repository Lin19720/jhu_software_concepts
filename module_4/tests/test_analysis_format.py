import pytest
import re

@pytest.mark.analysis
def test_analysis_labels_and_percentage_rounding(client):
    """测试分析输出结果包含 Answer 标签，且所有百分比均为两位小数格式"""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # 1. 验证 Answer 标签
    assert "Answer:" in html

    # 2. 匹配页面中所有的百分比数值（形如 12.34% 或 0.00%）
    percentages = re.findall(r"\b\d+\.\d+%", html)
    assert len(percentages) > 0, "页面中应至少包含一个格式化的百分比数据"

    for pct in percentages:
        # 提取小数点后面的数字串，校验其长度是否为 2
        decimals = pct.split(".")[1].replace("%", "")
        assert len(decimals) == 2, f"百分比格式未精确保留两位小数: {pct}"
