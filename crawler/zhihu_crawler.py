from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from db import get_conn
from service.analysis_service import analyze_all_articles


def log(msg):
    print(f"[Crawler] {msg}")
    conn = get_conn()
    cur = conn.cursor()

    # 如果是新任务的第一条日志，清空旧日志
    if "开始搜索关键词" in msg:
        cur.execute("TRUNCATE TABLE crawl_log")

    cur.execute(
        "INSERT INTO crawl_log (message) VALUES (%s)",
        (msg,)
    )

    conn.commit()
    cur.close()
    conn.close()

def add_log(msg):
    print(f"[Crawler] {msg}")
    conn = get_conn()
    cur = conn.cursor()

    # 如果是新任务的第一条日志，清空旧日志
    if "开始搜索关键词" in msg:
        cur.execute("TRUNCATE TABLE crawl_log")

    cur.execute(
        "INSERT INTO crawl_log (message) VALUES (%s)",
        (msg,)
    )

    conn.commit()
    cur.close()
    conn.close()


def run_crawler(keyword):
    conn = get_conn()
    cur = conn.cursor()

    # 1️⃣ 先删最底层表
    cur.execute("DELETE FROM keyword_weight")

    # 2️⃣ 再删情感分析表
    cur.execute("DELETE FROM sentiment_result")

    # 3️⃣ 最后删文章表
    cur.execute("DELETE FROM blog_article")

    conn.commit()
    cur.close()
    conn.close()
    log(f"开始搜索关键词：{keyword}")

    edge_options = Options()
    edge_options.add_experimental_option(
        "debuggerAddress", "127.0.0.1:9222"
    )

    wd = webdriver.Edge(options=edge_options)
    wd.implicitly_wait(5)

    # 1. 打开知乎搜索页
    search_url = f"https://www.zhihu.com/search?q={keyword}&type=content"
    wd.get(search_url)
    sleep(3)
    log("已进入知乎搜索页面")

    # 2. 滚动页面
    for i in range(2):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        log(f"页面滚动第 {i + 1} 次")

    # 3. 收集链接
    link_elements = wd.find_elements(By.CSS_SELECTOR, ".ContentItem-title a")
    urls = []

    for el in link_elements:
        href = el.get_attribute("href")
        if href and ("answer" in href or "p/" in href):
            if href not in urls:
                urls.append(href)

    log(f"共提取到 {len(urls)} 个链接，准备抓取前 10 个")

    # 4. 抓取正文并入库
    conn = get_conn()
    cur = conn.cursor()
    count = 0

    for url in urls:
        if count >= 10:
            break
        try:
            wd.get(url)
            sleep(4)

            title_el = wd.find_elements(
                By.CSS_SELECTOR,
                ".QuestionHeader-title, .Post-Title"
            )
            if not title_el:
                log("未获取到标题，跳过")
                continue

            title = title_el[0].text.strip()

            p_elements = wd.find_elements(By.CSS_SELECTOR, "p")
            content = "\n".join(
                [p.text for p in p_elements if p.text.strip()]
            )

            cur.execute(
                "INSERT INTO blog_article (title, content, url) VALUES (%s, %s, %s)",
                (title, content, url)
            )
            conn.commit()

            count += 1
            log(f"已抓取第 {count} 篇：{title[:20]}")

        except Exception as e:
            log(f"抓取失败：{e}")

    conn.close()
    wd.quit()
    log("爬虫任务完成")



