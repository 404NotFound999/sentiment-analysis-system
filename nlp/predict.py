from nlp.real_model import EmotionModel
from nlp.sentiment_labels import LABEL_MAP

# 全局加载一次模型（避免每次预测都加载）
_model = EmotionModel()


def predict_sentiment(text: str):
    label, confidence = _model.predict(text)

    return {
        "label": label,
        "label_name": LABEL_MAP[label],
        "confidence": round(confidence, 4)
    }