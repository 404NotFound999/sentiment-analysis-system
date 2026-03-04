import jieba

def tokenize(text: str):
    return [w for w in jieba.cut(text) if w.strip() and len(w) > 1]
