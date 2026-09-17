import json

def clean_record(r):
    # 1. 过滤 Quant（数学）分数：必须在 130 到 170 之间，把误抓的总分（>170）设为 None
    gre_q = r.get("gre") or r.get("gre_q")
    if gre_q is not None:
        try:
            val = float(gre_q)
            r["gre"] = val if 130 <= val <= 170 else None
        except (ValueError, TypeError):
            r["gre"] = None

    # 2. 过滤 Verbal（语文）分数：130 到 170
    gre_v = r.get("gre_v")
    if gre_v is not None:
        try:
            val = float(gre_v)
            r["gre_v"] = val if 130 <= val <= 170 else None
        except (ValueError, TypeError):
            r["gre_v"] = None

    # 3. 过滤 AW（写作）分数：0.0 到 6.0
    gre_aw = r.get("gre_aw")
    if gre_aw is not None:
        try:
            val = float(gre_aw)
            r["gre_aw"] = val if 0.0 <= val <= 6.0 else None
        except (ValueError, TypeError):
            r["gre_aw"] = None

    return r

# 读取并清洗数据
with open("llm_extend_applicant_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = [clean_record(item) for item in data]

# 写回清洗后的 JSON 文件
with open("llm_extend_applicant_data.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

with open("applicant_data.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print(f"[成功] 清洗完成！已修复 GRE 数值异常问题。")
