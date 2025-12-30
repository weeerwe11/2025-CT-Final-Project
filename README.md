# 英文小幫手

一個基於 **Ollama + 本地題庫** 的英文學習工具，支援文法修正、例句生成、單字解釋，以及選擇題練習模式。

---

## 專題目的

本專題旨在打造一個**輕量化、可擴充**的英文學習系統，結合：

* LLM（功能選擇、文法修正、解釋、例句）
* 本地題庫 (練習題)

---

## 環境架設

### 1️. 系統需求

* Python **3.10+**
* 可連線的 Ollama API Gateway

---

### 2️. Ollama 安裝與模型準備

本專案使用 **Ollama** 作為 LLM 執行環境，請先完成以下設定。

#### (1) 安裝 Ollama

請依照官方文件安裝 Ollama：

```text
https://ollama.com/download
```

安裝完成後，確認指令可正常執行：

```bash
ollama --version
```

---

#### (2) 下載模型（必要）

本專案預設使用以下模型：

```text
gemma3:4b
```

請先手動下載模型：

```bash
ollama pull gemma3:4b
```

> ⚠️ 若未下載模型，程式將無法呼叫 LLM API

---

#### (3) 模型設定說明

模型名稱定義於程式碼中：

```python
MODEL_NAME = "gemma3:4b"
```

若要更換模型，請確保：

* Ollama 中已下載該模型
* 模型名稱與 `MODEL_NAME` 一致

---

### 2️. Python 套件安裝

```bash
pip install ollama
```

（僅使用標準函式庫 + ollama client）

---

### 3️. API 設定

在程式中設定 API Key 與 Gateway：

```python
api_key = "YOUR_API_KEY"

client = Client(
    host="https://api-gateway.netdb.csie.ncku.edu.tw",
    headers={"Authorization": f"Bearer {api_key}"}
)
```

> ⚠️ 建議實務上改用環境變數，避免金鑰外洩

---

### 4️. 題庫格式（question.txt）

```text
He made a ____ recovery after the surgery, surprising the doctors.
A. painful
B. fantastic
C. risky
D. uncertain
Answer: B
```

* 題目區塊以「空行」分隔
* 必須包含 4 個選項（A–D）
* `Answer:` 為正確選項代號

---

## 功能說明

### 1️. 文法與拼字修正

輸入一個英文句子，系統會：

* 修正文法錯誤
* 改成自然英文

```text
>>> I wants learn English.
I want to learn English.
```

---

### 2️. 單字／片語例句生成

```text
>>> 給我 fantastic 的範例
Example: She did a fantastic job on the presentation.
```

---

### 3️. 單字／片語解釋

```text
>>> 解釋 fantastic
Fantastic means very good or excellent. It is often used to show strong approval.
```

---

### 4️. 題庫選擇題練習

```text
>>> 出一題
He made a ____ recovery after the surgery, surprising the doctors.
A. painful
B. fantastic
C. risky
D. uncertain
```

作答：

```text
Your answer: B
✅ Correct!
```

* 支援 A / B / C / D 作答
* 系統會記住當前題目狀態
* 可避免 LLM 延遲與成本

---

## 系統設計重點

* **Router 機制**：

  * 題庫指令 → 不呼叫 LLM
  * 語言處理 → 交由 LLM

* **狀態管理**：

  * `current_question` 控制作答流程

* **可擴充設計**：

  * 新增 Tool 只需加入方法 + Router 判斷

---

## 執行方式

```bash
python my_tool.py
```

```text
📘 LanguageTool (type 'exit' to quit)
>>>
```
