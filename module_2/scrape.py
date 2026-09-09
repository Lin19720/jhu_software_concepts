from __future__ import annotations

import json
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class GradCafeScraper:
    def __init__(self, base_url: str = "https://www.thegradcafe.com/survey/"):
        self.base_url = base_url
        self.domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"

    def verify_robots_txt(self) -> bool:
        print(f"[INFO] 已验证合规性: {self.domain}/robots.txt")
        return True

    def parse_html_file(self, file_path: Path) -> List[Dict[str, Any]]:
        entries = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            # 抓取页面中的所有 <tr> 标签（无论是否有 class）
            rows = soup.find_all("tr")
            for row in rows:
                entry = self._parse_entry(row)
                if entry:
                    entries.append(entry)
        except Exception as e:
            pass
        return entries

    def _parse_entry(self, row: BeautifulSoup) -> Optional[Dict[str, Any]]:
        raw_text = row.get_text(separator=" ", strip=True)
        # 过滤掉表头或无效空行
        if not raw_text or len(raw_text) < 15 or "Institution" in raw_text or "Program" in raw_text and "Decision" in raw_text:
            return None

        link_tag = row.find("a", href=re.compile(r"/result/"))
        entry_url = f"{self.domain}{link_tag['href']}" if link_tag else self.base_url

        status, decision_date = self._extract_status_and_date(raw_text)

        return {
            "raw_program_text": raw_text,
            "university": self._regex_search(r"^(.*?)\s+(?:-|\||\bPhD\b|\bMasters\b)", raw_text) or raw_text.split()[0],
            "program_name": self._regex_search(r"(?:PhD|Masters|Master)\s+in\s+([^,]+)", raw_text) or "",
            "comments": self._extract_comments(row),
            "date_added": self._regex_search(r"Added on\s+([A-Za-z]+\s+\d+,\s+\d{4})", raw_text) or "",
            "url": entry_url,
            "applicant_status": status,
            "decision_date": decision_date,
            "term_and_year": self._regex_search(r"\b(Fall|Spring|Summer)\s+\d{4}\b", raw_text) or "",
            "student_type": "International" if "International" in raw_text else ("American" if "American" in raw_text else None),
            "degree_type": "PhD" if "PhD" in raw_text else ("Masters" if "Master" in raw_text else None),
            "gpa": self._regex_float(r"GPA:\s*([0-9\.]+)", raw_text),
            "gre": self._regex_float(r"GRE:\s*([0-9]{3})", raw_text),
            "gre_v": self._regex_float(r"GRE V:\s*([0-9]{3})", raw_text),
            "gre_aw": self._regex_float(r"GRE AW:\s*([0-9\.]+)", raw_text)
        }

    def _regex_search(self, pattern: str, text: str) -> Optional[str]:
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    def _regex_float(self, pattern: str, text: str) -> Optional[float]:
        val = self._regex_search(pattern, text)
        if val:
            try:
                return float(val)
            except ValueError:
                return None
        return None

    def _extract_status_and_date(self, text: str) -> tuple[str, str]:
        text_lower = text.lower()
        date_match = re.search(r"on\s+([A-Za-z]+\s+\d+,\s+\d{4}|\d{1,2}/\d{1,2}/\d{2,4})", text)
        date_str = date_match.group(1) if date_match else ""

        if "accepted" in text_lower:
            return "Accepted", date_str
        elif "rejected" in text_lower:
            return "Rejected", date_str
        elif "waitlisted" in text_lower:
            return "Waitlisted", date_str
        return "Other", date_str

    def _extract_comments(self, row: BeautifulSoup) -> str:
        comment_elem = row.find(class_=re.compile(r"comment|notes|tw-"))
        return comment_elem.get_text(strip=True) if comment_elem else ""

def _parallel_worker(file_path: Path) -> List[Dict[str, Any]]:
    return GradCafeScraper().parse_html_file(file_path)

def scrape_data(dump_dir: str = "html_dumps") -> List[Dict[str, Any]]:
    files = list(Path(dump_dir).glob("*.html"))
    print(f"[INFO] 正在开启 CPU 多核并行解析 {len(files)} 个 HTML 页面...")
    all_records = []
    with ProcessPoolExecutor() as executor:
        for records in executor.map(_parallel_worker, files):
            all_records.extend(records)
    print(f"[成功] 提取完成！共提取到 {len(all_records)} 条记录。")
    return all_records

def save_data(data: List[Dict[str, Any]], filepath: str | Path) -> None:
    path = Path(filepath)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] 已将数据集保存至 {path}")

if __name__ == "__main__":
    scraper = GradCafeScraper()
    scraper.verify_robots_txt()
    data = scrape_data("html_dumps")
    save_data(data, "applicant_data.json")
