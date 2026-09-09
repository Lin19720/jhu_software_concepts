import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def capture_gradcafe_pages(start_page: int = 1, total_pages: int = 2500, output_dir: str = "html_dumps"):
    os.makedirs(output_dir, exist_ok=True)
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print(f"[INFO] 已成功连接至 Chrome 调试会话！准备抓取至第 {total_pages} 页...")
    except Exception as e:
        print(f"[错误] 无法连接到 Chrome，请先重新启动 Chrome 调试端口:\n{e}")
        return

    for page in range(start_page, start_page + total_pages):
        target_file = os.path.join(output_dir, f"page_{page}.html")
        
        # 断点续传：自动跳过已经下载好的页面
        if os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
            continue
            
        url = f"https://www.thegradcafe.com/survey/?p={page}"
        try:
            driver.get(url)
            time.sleep(0.5) # 稍微增加等待时间，减少浏览器压力
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                f.flush()
                
            print(f"[成功] 已保存第 {page} 页 -> {target_file}")
        except Exception as e:
            print(f"[警告] 第 {page} 页抓取异常，等待 3 秒后重试... 错误: {e}")
            time.sleep(3)

if __name__ == "__main__":
    capture_gradcafe_pages(start_page=1, total_pages=2500)
