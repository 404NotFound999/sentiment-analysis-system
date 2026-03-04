import torch
import torch.nn as nn
import jieba
import pickle
import os

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

num_classes = 7


# ===============================
# 1️⃣ 模型结构（必须和训练时完全一致）
# ===============================
class BiLSTMAttention(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True
        )
        self.attention = nn.Linear(hidden_dim * 2, 1)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x):
        embed = self.embedding(x)
        out, _ = self.lstm(embed)

        att = torch.softmax(self.attention(out).squeeze(-1), dim=1)
        context = torch.sum(out * att.unsqueeze(-1), dim=1)

        return self.fc(context)


# ===============================
# 2️⃣ 情绪预测类
# ===============================
class EmotionModel:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        vocab_path = os.path.join(BASE_DIR, "vocab.pkl")
        model_path = os.path.join(BASE_DIR, "emotion_model.pth")

        # 加载词表
        with open(vocab_path, "rb") as f:
            self.vocab = pickle.load(f)

        # 加载模型
        self.model = BiLSTMAttention(len(self.vocab))
        self.model.load_state_dict(
            torch.load(model_path, map_location=DEVICE)
        )
        self.model.to(DEVICE)
        self.model.eval()

    # ===============================
    # 3️⃣ 预测函数
    # ===============================
    def predict(self, text, max_len=100):

        words = jieba.lcut(text)
        ids = [self.vocab.get(w, 1) for w in words]  # 1 = <UNK>

        # padding / 截断
        if len(ids) < max_len:
            ids += [0] * (max_len - len(ids))  # 0 = <PAD>
        else:
            ids = ids[:max_len]

        x = torch.tensor([ids]).to(DEVICE)

        with torch.no_grad():
            output = self.model(x)
            prob = torch.softmax(output, dim=1)

            label = torch.argmax(prob, dim=1).item()
            confidence = prob[0][label].item()

        return label, confidence