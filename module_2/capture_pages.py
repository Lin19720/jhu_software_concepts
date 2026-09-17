import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def capture_gradcafe_pages(total_pages: int = 1200, output_dir: str = "html_dumps"):
    os.makedirs(output_dir, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    # 模拟真实浏览器参数
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    try:
        # 打开 Grad Cafe 首页
        print("[INFO] 正在打开 Grad Café 主页...")
        driver.get("https://www.thegradcafe.com/survey/")
        time.sleep(3)

        for page in range(1, total_pages + 1):
            target_file = os.path.join(output_dir, f"page_{page}.html")

            # 等待表格渲染成功
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "tr"))
            )
            time.sleep(1)

            # 保存当前页面的源码
            page_content = driver.page_source
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(page_content)
                f.flush()

            print(f"[成功] 保存第 {page}/{total_pages} 页 -> {target_file} ({len(page_content)} bytes)")

            # 尝试点击 "Next" 或 ">" 分页按钮
            try:
                # 寻找包含 next / > 的分页按钮
                next_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next') or contains(text(), '›') or contains(@aria-label, 'Next')]")
                if not next_buttons:
                    next_buttons = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li:last-child a")
                
                if next_buttons and next_buttons[0].is_enabled():
                    # 滚动到按钮位置并点击
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_buttons[0])
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", next_buttons[0])
                    time.sleep(1.5)  # 等待 AJAX 加载新数据
                else:
                    print("[提示] 已经到达最后一页，停止抓取。")
                    break
            except Exception as e:
                print(f"[警告] 点击下一页失败: {e}，正在尝试刷新后继续...")
                time.sleep(2)

    finally:
        driver.quit()

if __name__ == "__main__":
    capture_gradcafe_pages(total_pages=1200)
