# 🍌 PaperBanana

輸入一段方法論的文字描述，產出論文風格的方法論示意圖。本機執行、單一檔案、Windows 雙擊即開。

## ⚠️ 先搞清楚兩件事

這個 repo 裡有**兩種完全不同的東西**，很容易搞混：

| 檔案 | 是什麼 | 怎麼用 |
|---|---|---|
| `index.html` | **靜態展示頁**：專案介紹 + 實際輸出範例圖 | 用瀏覽器直接打開，或看線上的 GitHub Pages |
| `PaperBanana.py` | **真正的工具**：Flask 網頁應用（跑在 5051 埠） | 需要 Python 環境 + API Key，`python PaperBanana.py` |

`index.html` **不是**這個工具的使用介面，也不會由 Python 產生。
執行 `PaperBanana.py` 時，介面是寫在 Python 裡直接由 Flask 提供的。

換句話說：

- 想「看這個專案在做什麼」→ 打開 `index.html`
- 想「真的生成圖片」→ 執行 `PaperBanana.py`（本站靜態頁做不到）

## 快速開始

```bash
# 1. 安裝相依套件
pip install flask paperbanana

# 2. 放入 OpenRouter API Key（二選一）
#    a) 在資料夾建立 .openrouter_key，內容只放金鑰那一行
#    b) 把金鑰貼進 PaperBanana.py 最上面的 KEY_CONTENT 變數

# 3. 啟動（Windows 可直接雙擊 PaperBanana.bat）
python PaperBanana.py

# 4. 瀏覽器會自動開啟 http://localhost:5051
```

操作方式：在文字框輸入描述（中英文皆可）→ 設定 Refine 次數（1～10）→ 按 Generate。

每次生成會在 `pb_output/runs/` 下建立一個資料夾，保留每一輪的圖片與規劃紀錄。

## 運作流程

```
你輸入描述
   ↓
視覺規劃  google/gemini-2.5-flash          ← 把文字翻成版面規劃書
   ↓
圖像生成  google/gemini-3.1-flash-lite-image ← 依規劃書繪圖
   ↓
精煉迭代  重複「檢查 → 改寫規劃 → 重畫」N 次
   ↓
最終輸出  pb_output/runs/<run_id>/final_output.png
```

## 費用提醒

每次按下 Generate 都會實際呼叫 OpenRouter API 並產生費用，金額與 Refine 次數成正比。次數越多圖越細緻，但花費也等比增加。

## 出處與致謝

方法論來自論文 **PaperBanana: Automating Academic Illustration for AI Scientists**
（Dawei Zhu, Rui Meng, Yale Song, Xiyu Wei, Sujian Li, Tomas Pfister, Jinsung Yoon，
arXiv:2601.23265，Google Cloud AI Research / 北京大學），原始框架後續以
**PaperVizAgent** 之名開源於 Google Research。

本 repo 是基於該論文與公開的 `paperbanana` 套件所做的**個人單機版整合**，
保留最核心的「規劃 → 生成 → 精煉」循環，加上 Windows 一鍵啟動與繁體中文介面。
本專案與原作者、Google 無隸屬或背書關係。學術引用請引用原論文。

## 授權

本 repo 的整合層程式碼為個人專案。底層方法論與套件請依其原始授權使用。
