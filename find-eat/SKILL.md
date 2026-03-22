# 🍽️ Find Eat Skill

## 觸發條件
用戶問搵食、推介餐廳、約飯地點、lunch/dinner 去邊好、附近有咩食

---

## 流程總覽

```
抽取條件 → 排除 closed/blacklist → 查 verified cache → 搜尋 OpenRice → 驗證營業 → 評分排序 → 輸出 → 更新 cache
```

---

## Step 1: 抽取條件

先確保有以下資訊，唔夠就問：

| 條件 | 必須？ | Default |
|------|--------|---------|
| **地區** | ✅ 必須 | 問用戶 |
| **預算/位** | 建議 | $100-300 |
| **人數** | 建議 | 4人 |
| **場合** | 建議 | 朋友聚餐 |
| **菜式** | 可選 | 隨意 |
| **時間** | 可選 | dinner |
| **特殊需求** | 可選 | 無（素食、敏感、BB椅等）|

條件唔完整時，用合理 default 先搵，唔好死等用戶答晒。

### 中間點計算（兄弟群 mode）
如果係兄弟約食飯但未定地區：

| 人 | 住 | 方便嘅 MTR 站 |
|---|---|---|
| Peter | 青衣 | 青衣、荃灣、荔景 |
| Philip | 荃灣 | 荃灣 |
| 古大俠 | - | 問 |
| Ken | - | 問 |
| Koon | - | 識搵食，聽佢 |

**推薦邏輯：**
- 2-3 人 → 就近其中一方
- 4+ 人 → 搵中間交匯點（荃灣/旺角/中環 通常最方便）
- 有 Koon 出席 → 優先問佢推介

---

## Step 2: 排除唔推介嘅餐廳

讀取以下 JSON files（skill 目錄下）：
- `closed.json` — 已結業，唔存在
- `blacklist.json` — 食過但差，唔推介
- `wrong_district.json` — 過去搞錯地區嘅記錄

---

## Step 3: 查 Verified Cache

讀 `verified.json`，睇有冇符合條件嘅已驗證餐廳。

**Match 條件：** 地區 + 菜式 + 預算範圍
**如有 ≥3 間符合 → 直接用 cache 推介，跳 Step 4**
**仍需跑 Step 5 驗證營業狀態**（verified 唔代表永遠開）

---

## Step 4: 搜尋（OpenRice 為金標準 🏆）

### 4A: OpenRice 搜尋（Primary — 必做）

```bash
# 主搜尋 — OpenRice 結果
npx mcporter call tavily tavily_search \
  query="site:openrice.com [菜式] [地區] 推介 餐廳" \
  max_results=10

# 補充搜尋 — 加年份確保新鮮
npx mcporter call tavily tavily_search \
  query="openrice [地區] [菜式] [場合] 推介 2025 2026" \
  max_results=5
```

### 4B: OpenRice 詳情頁抓取（每間候選餐廳）

OpenRice 需要 JS rendering，用 browser tool：

```
# 用 browser tool 打開 OpenRice 頁面
browser → navigate to openrice.com/zh/hongkong/r-[name]-[district]-[cuisine]-r[ID]
browser → snapshot → 抽取：
  - 餐廳名（中/英）
  - 地址
  - 電話
  - 營業時間
  - OpenRice 評分（食物/環境/服務/衛生）
  - 人均消費
  - 「已結業」標記
  - 最近食評日期
  - 訂座連結
```

**如果 browser tool 唔可用，fallback 到 Tavily：**
```bash
npx mcporter call tavily tavily_search \
  query="openrice [餐廳名] [地區] 評分 地址 電話" \
  max_results=3
```

### 4C: 補充搜尋（Secondary）

```bash
# Google 搜尋驗證
npx mcporter call tavily tavily_search \
  query="[餐廳名] [地區] 香港 2025 2026 食評 review" \
  max_results=3

# IG/社交媒體驗證（optional，確認仲有人食緊）
npx mcporter call tavily tavily_search \
  query="[餐廳名] instagram OR 小紅書 2025 2026" \
  max_results=2
```

---

## Step 5: 三源驗證（每間推介必做 ⚠️）

**唔確認係咪仍然營業，唔好推介！**

| 來源 | 查咩 | 結業信號 |
|------|------|---------|
| **OpenRice** 🏆 | 頁面有冇「已結業」 | ❌ 「已結業 Closed」標記 |
| **Google** | 搜尋餐廳名 | ❌ 「Permanently closed」 |
| **近期食評** | 最近 6 個月有冇新食評 | ⚠️ 超過 12 個月冇食評 = 高風險 |

```bash
# 結業驗證搜尋
npx mcporter call tavily tavily_search \
  query="[餐廳名] [地區] 結業 closed permanently closed 2025 2026" \
  max_results=3
```

### 判定規則
- **三源都冇結業信號 + 有近期食評** → ✅ 確認營業
- **任何一源顯示結業** → ❌ 移入 `closed.json`，唔推介
- **冇結業信號但 12+ 個月冇食評** → ⚠️ 標記「未能完全確認」
- **地址/地區有歧義** → 交叉驗證，如有錯記入 `wrong_district.json`

---

## Step 6: 評分排序

### OpenRice 評分權重（金標準）

| 維度 | 權重 | 說明 |
|------|------|------|
| 食物質素 | 40% | 最重要 |
| 環境 | 25% | 場合相關 |
| 服務 | 20% | 體驗 |
| 衛生 | 15% | 基本要求 |

### 額外加分/減分

| 因素 | 調整 |
|------|------|
| 在 `verified.json`（兄弟食過好） | +15% |
| 最近 3 個月有大量好評 | +10% |
| 有訂座服務 | +5% |
| 預算超出用戶範圍 | -20% |
| 近期有差評（衛生/服務）| -15% |
| 排隊時間 > 30min | -10%（標注） |

---

## Step 7: 輸出格式

```
🍽️ [場合] 推介 — [地區] / [預算]/位

1. **[餐廳名]** ✅ 已確認營業
   📍 [地址]
   💰 人均 $[X]
   ⭐ OpenRice: 食物 [X] / 環境 [X] / 服務 [X] / 衛生 [X]
   🎭 [一句話描述氛圍/適合場合]
   📞 [電話] | 🔗 [OpenRice link]
   💡 [點解推呢間 — 一句]

2. ...

3. ...

---
🏆 推薦：[哪間最適合今次場合，一句理由]
📅 訂位：[訂位方法/link]
⏰ 建議時間：[lunch 12:00-13:30 / dinner 19:00-20:30]
🚇 交通：[最近 MTR 站 + 步行時間]
```

### 附近有咩食 Mode
如果用戶問「附近有咩食」/ 冇特定要求：
- 唔好列太多選項（3-4間夠）
- 注重多樣性（唔好全部同一菜式）
- 標注步行時間

---

## Step 8: 更新 Cache

### 自動更新
| 情況 | 動作 |
|------|------|
| 確認營業 + 有 OpenRice 數據 | 更新/加入 `verified.json` |
| 發現結業 | 加入 `closed.json` |
| 地區錯誤 | 加入 `wrong_district.json` |

### Feedback Loop（食完回報）
當 Peter 或兄弟食完 report：
- 「好食」→ 更新 `verified.json` rating + 加 `last_visited` 日期
- 「唔好」→ 加入 `blacklist.json` 加原因
- 「結咗業」→ 移入 `closed.json`

**觸發詞：**「上次嗰間好好食」「唔好食」「好難食」「結業咗」「執笠」「唔推介」

---

## Step 9: 時令 & 天氣考慮

| 季節/天氣 | 考慮 |
|-----------|------|
| 🌧️ 落雨 | 優先室內、唔使排隊、有蓋 |
| 🥵 夏天 (6-9月) | 有冷氣、唔好 outdoor |
| 🦀 秋天 (9-11月) | 大閘蟹季、蛇羹 |
| 🎄 聖誕/新年 | 要提早訂、留意特別 menu |
| 🧧 農曆新年 | 好多餐廳休息，提前確認 |
| 🌸 春天 | Outdoor dining OK |

### 自動天氣 check
推介前 check 天氣：
```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
```
如果落大雨/颱風 → 優先推介唔使排隊、近 MTR 嘅選擇

---

## JSON Schema

### verified.json
```json
{
  "last_updated": "2026-03-22",
  "restaurants": [
    {
      "name": "大班樓",
      "name_en": "The Chairman",
      "district": "中環",
      "address": "中環九如坊18號",
      "cuisine": "粵菜",
      "budget_pp": 800,
      "openrice_id": "r56578",
      "openrice_url": "https://www.openrice.com/zh/hongkong/r-the-chairman-central-cantonese-r56578",
      "openrice_rating": {"food": 4.2, "ambience": 4.0, "service": 4.1, "hygiene": 4.0},
      "phone": "2555-2202",
      "nearest_mtr": "中環站 D2 出口",
      "walk_mins": 5,
      "good_for": ["商務", "慶祝", "拍拖"],
      "notes": "要預早訂位",
      "last_verified": "2026-03-22",
      "last_visited": null,
      "visited_by": [],
      "verdict": null
    }
  ]
}
```

### closed.json
```json
{
  "last_updated": "2026-03-22",
  "restaurants": [
    {
      "name": "Wooloomooloo Steakhouse",
      "district": "中環",
      "address": "雲咸街29號 Onfem Tower",
      "cuisine": "西餐",
      "closed_date": "2025 或之前",
      "source": "OpenRice 顯示 Closed",
      "notes": "灣仔同尖沙咀分店仲開緊",
      "discovered_date": "2026-02-25"
    }
  ]
}
```

### blacklist.json
```json
{
  "last_updated": "2026-03-22",
  "restaurants": [
    {
      "name": "Example",
      "district": "旺角",
      "reason": "服務差，等咗成個鐘",
      "visited_by": "Peter",
      "visited_date": "2026-01-15",
      "added_date": "2026-01-15"
    }
  ]
}
```

### wrong_district.json
```json
{
  "last_updated": "2026-03-22",
  "corrections": [
    {
      "name": "明閣 Ming Court",
      "claimed_district": "中環",
      "actual_district": "旺角",
      "address": "旺角朗廷酒店",
      "notes": "AI 經常搞錯",
      "discovered_date": "2026-02-25"
    }
  ]
}
```

---

## 場合 Vibe 指引

| 場合 | 關鍵字 | 避免 |
|------|--------|------|
| 商務 lunch | 安靜、有格調、服務好、快 | 太嘈、大牌檔 |
| 兄弟 hea 聚 | 夠食、夠飲、唔趕客、抵食 | 太正式、貴到肉赤 |
| 慶祝 / 退休 | 有儀式感、高級、影相靚 | 連鎖快餐 |
| 家庭 / 有細路 | 空間大、唔怕嘈、有BB椅 | 太 fine dining |
| 拍拖 | 氣氛、燈光、私密 | 大圍枱、嘈雜 |
| 快食 | 出餐快、唔使排隊 | 需要等位 |
| 養生 | 清淡、有機、走味精 | 重口味 |

---

## 重要原則 ⚠️

1. **OpenRice 係金標準** — 所有推介必須有 OpenRice 頁面/資料支持
2. **唔確認營業，唔好推介** — 三源驗證，零妥協
3. **注意地區正確** — 交叉驗證地址，錯過就記低
4. **價格要 update** — 舊 review 價錢唔準，盡量搵最近嘅
5. **OpenRice link 格式** — `openrice.com/zh/hongkong/r-[name]-[district]-[cuisine]-r[ID]`
6. **唔好推介冇 OpenRice 記錄嘅餐廳** — 如果 OpenRice 搵唔到，唔夠可信
7. **每次推介後更新 cache** — 呢個係知識庫，越用越準
