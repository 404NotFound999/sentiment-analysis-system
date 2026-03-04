from db import get_conn
from nlp.predict import predict_sentiment
from nlp.tokenizer import tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


def analyze_all_articles():
    conn = get_conn()
    cur = conn.cursor()

    try:
        # 1️⃣ 取所有文章
        cur.execute("SELECT id, content FROM blog_article")
        articles = cur.fetchall()

        if not articles:
            print("[Analysis] ⚠️ 没有文章可分析")
            return

        # 2️⃣ 全量文本（用于 TF-IDF）
        texts = []
        article_ids = []

        for article_id, content in articles:
            words = tokenize(content)
            texts.append(" ".join(words))
            article_ids.append(article_id)

        # 3️⃣ TF-IDF（不限制特征数）
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)

        keywords = vectorizer.get_feature_names_out()

        # 4️⃣ 每篇文章写入所有关键词权重
        for idx, article_id in enumerate(article_ids):
            weights = tfidf_matrix[idx].toarray()[0]

            for word, weight in zip(keywords, weights):
                if weight == 0:
                    continue

                cur.execute("""
                    INSERT INTO keyword_weight (article_id, keyword, weight)
                    VALUES (%s, %s, %s)
                """, (article_id, word, float(weight)))

            # 情感分析（单篇）
            result = predict_sentiment(articles[idx][1])
            cur.execute("""
                INSERT INTO sentiment_result (article_id, label, label_name, confidence)
                VALUES (%s, %s, %s, %s)
            """, (
                article_id,
                result["label"],
                result["label_name"],
                result["confidence"]
            ))

        conn.commit()
        print("[Analysis] ✅ 全量分析完成")

    except Exception as e:
        conn.rollback()
        print("[Analysis] ❌ 分析失败：", e)

    finally:
        cur.close()
        conn.close()

