import pandas as pd
import torch
import jieba
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import pickle

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===============================
# 1️⃣ 标签映射
# ===============================
label_map = {
    "anger": 0,
    "disgust": 1,
    "fear": 2,
    "sadness": 3,
    "happiness": 4,
    "like": 5,
    "surprise": 6
}

num_classes = 7


# ===============================
# 2️⃣ 数据集类
# ===============================
class EmotionDataset(Dataset):
    def __init__(self, texts, labels, vocab, max_len=100):
        self.texts = texts
        self.labels = labels
        self.vocab = vocab
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        words = jieba.lcut(self.texts[idx])
        ids = [self.vocab.get(w, 1) for w in words]

        if len(ids) < self.max_len:
            ids += [0] * (self.max_len - len(ids))
        else:
            ids = ids[:self.max_len]

        return torch.tensor(ids), torch.tensor(self.labels[idx])


# ===============================
# 3️⃣ 模型
# ===============================
class BiLSTMAttention(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attention = nn.Linear(hidden_dim*2, 1)
        self.fc = nn.Linear(hidden_dim*2, num_classes)

    def forward(self, x):
        embed = self.embedding(x)
        out, _ = self.lstm(embed)

        att = torch.softmax(self.attention(out).squeeze(-1), dim=1)
        context = torch.sum(out * att.unsqueeze(-1), dim=1)

        return self.fc(context)


# ===============================
# 4️⃣ 训练函数
# ===============================
def train_model(train_loader, val_loader, model, epochs=10):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    model.to(DEVICE)

    for epoch in range(1, epochs+1):
        model.train()
        total_loss = 0

        for x, y in train_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)

            optimizer.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch} Train Loss: {total_loss/len(train_loader):.4f}")

        # 验证
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                pred = model(x)
                pred_label = torch.argmax(pred, dim=1)
                correct += (pred_label == y).sum().item()
                total += len(y)

        print(f"Epoch {epoch} Val Acc: {correct/total:.4f}")


# ===============================
# 5️⃣ 主程序
# ===============================
if __name__ == "__main__":
    df = pd.read_csv("Nlpcc2014Train.csv")

    texts = df["文本"].astype(str).tolist()
    labels = [label_map[l] for l in df["标签"]]

    # 构建词表
    word_freq = {}
    for t in texts:
        for w in jieba.lcut(t):
            word_freq[w] = word_freq.get(w, 0) + 1

    vocab = {"<PAD>":0, "<UNK>":1}
    for w,_ in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10000]:
        vocab[w] = len(vocab)

    X_train, X_val, y_train, y_val = train_test_split(texts, labels, test_size=0.2)

    train_ds = EmotionDataset(X_train, y_train, vocab)
    val_ds = EmotionDataset(X_val, y_val, vocab)

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64)

    model = BiLSTMAttention(len(vocab))

    train_model(train_loader, val_loader, model)

    torch.save(model.state_dict(), "emotion_model.pth")

    with open("vocab.pkl", "wb") as f:
        pickle.dump(vocab, f)

    print("模型和词表已保存！")