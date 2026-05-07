from playwright.sync_api import sync_playwright
import re
import json
import os

def get_d1ev_news():
    """
    专门用于 GitHub Actions 调试的爬虫函数。
    输出结果会保存到文件，方便查看。
    """
    print("📡 正在启动浏览器环境，访问第一电动网快讯...")
    news_list = []
    
    with sync_playwright() as p:
        try:
            # GitHub Actions 环境必须使用 headless=True
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            print("⏳ 正在加载页面...")
            page.goto("https://www.d1ev.com/newsflash", timeout=60000)
            
            # 等待页面加载
            page.wait_for_load_state("networkidle")
            
            # 获取页面标题，确认页面加载成功
            page_title = page.title()
            print(f"📄 页面标题: {page_title}")
            
            # 获取页面内容
            html = page.content()
            browser.close()
            
            # 保存 HTML 到文件（方便调试查看）
            with open("page_content.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"💾 已保存页面 HTML 到 page_content.html")
            
            # 解析新闻
            # 尝试多种匹配模式
            patterns = [
                r'<a[^>]+data-id="\d+"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                r'<a[^>]+href="(/newsflash/\d+)"[^>]*>(.*?)</a>',
                r'class="[^"]*strike-item[^"]*"[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                print(f"🔍 使用模式 {patterns.index(pattern)+1}: 找到 {len(matches)} 个匹配")
                
                if matches:
                    break
            
            seen_urls = set()
            base_url = "https://www.d1ev.com"
            
            for href, title_html in matches:
                # URL 处理
                if href.startswith("//"):
                    url = "https:" + href
                elif href.startswith("/"):
                    url = base_url + href
                else:
                    url = href
                
                # 去重
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                # 标题清洗
                title = re.sub(r'<[^>]+>', '', title_html)
                title = re.sub(r'\s+', ' ', title).strip()
                
                if len(title) < 5:
                    continue
                
                news_list.append({
                    "title": title,
                    "url": url,
                    "summary": ""
                })
                
                if len(news_list) >= 10:
                    break
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            # 保存错误信息
            with open("error_log.txt", "w") as f:
                f.write(f"Error: {str(e)}\n")
            return []
    
    # 保存结果到 JSON 文件
    with open("debug_result.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    
    print(f"🎉 调试完成。共成功抓取 {len(news_list)} 条有效新闻。")
    return news_list

if __name__ == "__main__":
    news = get_d1ev_news()
    
    print("\n" + "="*50)
    print("最终调试结果预览:")
    for idx, item in enumerate(news, 1):
        print(f"{idx}. [{item['title']}]({item['url']})")
