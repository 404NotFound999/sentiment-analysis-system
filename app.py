from flask import Flask, render_template, request, jsonify
from crawler.zhihu_crawler import run_crawler
from db import get_conn
import threading
import pymysql
from datetime import datetime
from service.analysis_service import analyze_all_articles


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/crawl")
def crawl_page():
    return render_template("crawling.html")


@app.route("/start_crawl", methods=["POST"])
def start_crawl():
    data = request.get_json()
    keyword = data.get("keyword")

    print(f"[Flask] 收到爬虫请求 URL: {keyword}")

    t = threading.Thread(target=run_crawler, args=(keyword,))
    t.start()

    return jsonify({"status": "ok"})


@app.route("/get_progress")
def get_progress():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT message FROM crawl_log ORDER BY id DESC LIMIT 50")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/manual')
def manual_page():
    return render_template('/manual.html')


@app.route("/manual/submit", methods=["POST"])
def manual_submit():
    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"msg": "正文不能为空"}), 400

    conn = get_conn()
    cur = conn.cursor()

    try:
        # 1️⃣ 入库
        cur.execute("""
            INSERT INTO blog_article (title, content)
            VALUES (%s, %s)
        """, (title, content))

        article_id = cur.lastrowid   # ⭐ 关键
        conn.commit()

        print(f"[Manual] ✅ 人工文本已入库，ID={article_id}")

        # 2️⃣ 立刻做 NLP 分析
        analyze_all_articles()

        # 3️⃣ 返回 article_id 给前端
        return jsonify({
            "msg": "ok",
            "article_id": article_id
        })

    except Exception as e:
        conn.rollback()
        print("[Manual] ❌ 入库失败：", e)
        return jsonify({"msg": "error"}), 500

    finally:
        cur.close()
        conn.close()



@app.route("/analysis")
def analysis_page():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # ---------- 情感统计 ----------
    cur.execute("""
        SELECT label_name, COUNT(*) AS count
        FROM sentiment_result
        GROUP BY label_name
    """)
    sentiment_stats = cur.fetchall()

    # ---------- 关键词 Top10（全量） ----------
    cur.execute("""
        SELECT keyword, SUM(weight) AS weight
        FROM keyword_weight
        GROUP BY keyword
        ORDER BY weight DESC
        LIMIT 10
    """)
    keywords = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        sentiment_stats=sentiment_stats,
        keywords=keywords
    )
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/articles_with_sentiment")
def articles_with_sentiment():
    conn = get_conn()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 联合查询 blog_article 和 sentiment_result
    cur.execute("""
        SELECT b.id, b.title, b.content, s.label_name
        FROM blog_article b
        LEFT JOIN sentiment_result s ON b.id = s.article_id
        ORDER BY b.id ASC
    """)
    articles = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(articles)

@app.route("/api/sentiment_stats")
def sentiment_stats():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT label_name, COUNT(*) 
        FROM sentiment_result 
        GROUP BY label_name
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "labels": [row[0] for row in data],
        "counts": [row[1] for row in data]
    })

@app.route("/api/top_keywords")
def top_keywords():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT keyword, SUM(weight) as total_weight
        FROM keyword_weight
        GROUP BY keyword
        ORDER BY total_weight DESC
        LIMIT 20
    """)
    data = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "keywords": [row[0] for row in data],
        "weights": [float(row[1]) for row in data]
    })

@app.route("/analysis/run")
def run_analysis():
    analyze_all_articles()
    return jsonify({"msg": "ok"})

if __name__ == "__main__":
    print("[Flask] piggyboo 启动成功")
    app.run(debug=True)
