# 香港 AI 日報

手機優先、純靜態，畀香港的 Scott。版面喺 `index.html`（CSS／JS 內嵌），**當日內容喺頂層 `data.json`**。頁面用 `fetch('data.json')` 載入，無 build step、無 framework。

Live：https://ctang613.github.io/scott-ai-news/

介面用繁體中文同廣東話標籤。`updatedAt` 係一個帶時區偏移的時間戳，頁面一律用 `Asia/Hong_Kong` 顯示做「香港時間」。

## 今期

`data.json` 的 `edition` 係 **2026-10-05**。三欄各 5 則：

| 欄 | 內容 |
| --- | --- |
| `mustKnow` | 一定要知：模型有冇真正開放、監管、主權模型 |
| `tech` | 技術：決策模型、上下文／價錢、基準同任務成本 |
| `skills` | 技能：落手之前可以做的五件事實 |

每則可以有 `image` 同 `imageAlt`。有來源預覽圖就放本地檔（原文 og:image），冇就用 `assets/images/` 入面的插圖。來源標誌喺 `assets/logos/`。欄位見 [`schema/digest.schema.json`](schema/digest.schema.json)。

## 本機開啟

`data.json` 要經 HTTP 先載入到，**唔好直接雙擊 `index.html`（`file://` 會載入失敗）**。

```bash
python3 scripts/check_data.py
python3 -m http.server 8000
```

然後開 http://localhost:8000 。

## 更新資料

改 `data.json` 之後跑：

```bash
python3 scripts/check_data.py
```

檢查器要求 `edition` 同 `asOf` 都係 `2026-10-05`，`updatedAt` 換算做香港時間之後仍然係呢一日，而且 `mustKnow`、`tech`、`skills` 各有剛好 5 則。每則要有 `id`、`title`、`summary`、`source`、`url`（https）、`published`。如果有 `image`，就要同時有 `imageAlt`，而且本地路徑一定要係真實檔案。

## 發佈

`main` 分支根目錄就係 GitHub Pages 的來源。Push 上 `main` 之後，頁面會由 https://ctang613.github.io/scott-ai-news/ 提供。repo 根目錄有 `.nojekyll`，避免 Jekyll 處理。
