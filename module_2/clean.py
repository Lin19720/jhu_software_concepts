import json
import requests
from pathlib import Path

LLM_API_URL = "http://127.0.0.1:8000/clean"

def clean_data(input_file="applicant_data.json", output_file="llm_extend_applicant_data.json"):
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"[错误] 找不到输入文件: {input_file}")
        return

    print(f"[INFO] 正在读取 {input_file}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[INFO] 开始处理 {len(data)} 条记录...")
    
    cleaned_data = []
    for idx, entry in enumerate(data):
        university = entry.get("university", "")
        program = entry.get("program_name", "")
        
        # 补充清洗字段：尝试调用 LLM 标准化，若接口未对齐则回退至提取值
        try:
            resp = requests.post(LLM_API_URL, json={"university": university, "program": program}, timeout=2)
            if resp.status_code == 200:
                res = resp.json()
                entry["cleaned_university"] = res.get("cleaned_university", university)
                entry["cleaned_program"] = res.get("cleaned_program", program)
            else:
                entry["cleaned_university"] = university
                entry["cleaned_program"] = program
        except Exception:
            entry["cleaned_university"] = university
            entry["cleaned_program"] = program

        cleaned_data.append(entry)

        if (idx + 1) % 10000 == 0:
            print(f"[进度] 已清洗 {idx + 1} / {len(data)} 条数据...")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"[成功] 清洗完成！最终交付文件已保存至: {output_file}")

if __name__ == "__main__":
    clean_data()
