# 🍽️ Find Eat Skill

## Trigger
User asks to find restaurants, recommend places to eat, lunch/dinner suggestions, or "what's nearby to eat".

**Designed for Hong Kong 🇭🇰** — OpenRice is the golden reference.

---

## Flow Overview

```
Extract criteria → Exclude closed/blacklist → Check verified cache → Search OpenRice → Verify open → Score & rank → Output → Update cache
```

---

## Step 1: Extract Criteria

Ensure you have the following, ask if missing:

| Criteria | Required? | Default |
|----------|-----------|---------|
| **District** | ✅ Yes | Ask user |
| **Budget/person** | Recommended | $100-300 |
| **Party size** | Recommended | 4 |
| **Occasion** | Recommended | Friends gathering |
| **Cuisine** | Optional | Any |
| **Time** | Optional | Dinner |
| **Special needs** | Optional | None (vegetarian, allergies, baby chair, etc.) |

Don't wait for every answer — use reasonable defaults and search first.

### Midpoint Calculation (Group Mode)
If a group of friends needs to meet but hasn't decided on a district:
- **2-3 people** → go near one person's location
- **4+ people** → find a central MTR interchange point
- If someone in the group is a foodie expert, ask them first

---

## Step 2: Exclude Restaurants

Read these JSON files (in skill directory):
- `closed.json` — permanently closed
- `blacklist.json` — visited but bad, don't recommend
- `wrong_district.json` — past district misidentification records

---

## Step 3: Check Verified Cache

Read `verified.json` for previously verified restaurants matching criteria.

**Match on:** district + cuisine + budget range
**If ≥3 matches → use cache, skip to Step 5** (still verify they're open)

---

## Step 4: Search (OpenRice is the Golden Standard 🏆)

### 4A: OpenRice Search (Primary — mandatory)

```
# Primary search — OpenRice results
search: "site:openrice.com [cuisine] [district] 推介 餐廳"

# Supplementary — with year for freshness
search: "openrice [district] [cuisine] [occasion] 推介 [current year]"
```

### 4B: OpenRice Detail Page (per candidate restaurant)

OpenRice requires JS rendering — use browser tool if available:

```
browser → navigate to openrice.com/zh/hongkong/r-[name]-[district]-[cuisine]-r[ID]
browser → snapshot → extract:
  - Restaurant name (Chinese/English)
  - Address
  - Phone
  - Opening hours
  - OpenRice rating (food/ambience/service/hygiene)
  - Average spend per person
  - "Closed" marker
  - Latest review date
  - Booking link
```

**If browser tool unavailable, fallback to web search:**
```
search: "openrice [restaurant name] [district] 評分 地址 電話"
```

### 4C: Supplementary Search (Secondary)

```
# Google verification
search: "[restaurant name] [district] Hong Kong [current year] review"

# Social media verification (optional — confirm people are still visiting)
search: "[restaurant name] instagram OR 小紅書 [current year]"
```

---

## Step 5: 3-Source Verification (MANDATORY for every recommendation ⚠️)

**Never recommend without confirming it's still open!**

| Source | Check | Closure Signal |
|--------|-------|----------------|
| **OpenRice** 🏆 | Page has "已結業" marker? | ❌ "已結業 Closed" label |
| **Google** | Search restaurant name | ❌ "Permanently closed" |
| **Recent reviews** | Any reviews in last 6 months? | ⚠️ >12 months no reviews = high risk |

```
# Closure verification search
search: "[restaurant name] [district] 結業 closed permanently closed [current year]"
```

### Verdict Rules
- **All 3 sources clear + recent reviews** → ✅ Confirmed open
- **Any source shows closed** → ❌ Add to `closed.json`, don't recommend
- **No closure signal but 12+ months no reviews** → ⚠️ Flag "unable to fully confirm"
- **Address/district ambiguity** → Cross-verify, log errors in `wrong_district.json`

---

## Step 6: Scoring & Ranking

### OpenRice Rating Weights (Golden Standard)

| Dimension | Weight | Notes |
|-----------|--------|-------|
| Food quality | 40% | Most important |
| Ambience | 25% | Occasion-dependent |
| Service | 20% | Experience |
| Hygiene | 15% | Baseline requirement |

### Bonus / Penalty

| Factor | Adjustment |
|--------|------------|
| In `verified.json` (previously verified good) | +15% |
| Many good reviews in last 3 months | +10% |
| Has booking service | +5% |
| Over user's budget | -20% |
| Recent bad reviews (hygiene/service) | -15% |
| Queue time > 30min | -10% (flag it) |

---

## Step 7: Output Format

```
🍽️ [Occasion] Picks — [District] / [Budget]/person

1. **[Restaurant Name]** ✅ Confirmed open
   📍 [Address]
   💰 Avg $[X]/person
   ⭐ OpenRice: Food [X] / Ambience [X] / Service [X] / Hygiene [X]
   🎭 [One-line vibe description]
   📞 [Phone] | 🔗 [OpenRice link]
   💡 [Why this pick — one line]

2. ...

3. ...

---
🏆 Top pick: [which one & why]
📅 Booking: [method/link]
⏰ Suggested time: [lunch 12:00-13:30 / dinner 19:00-20:30]
🚇 Transport: [nearest MTR + walk time]
```

### "What's Nearby" Mode
If user asks "what's nearby" / no specific requirements:
- Keep it short (3-4 options max)
- Prioritize variety (don't recommend all same cuisine)
- Include walk time

---

## Step 8: Update Cache

### Auto-update
| Situation | Action |
|-----------|--------|
| Confirmed open + have OpenRice data | Update/add to `verified.json` |
| Found closed | Add to `closed.json` |
| District error | Add to `wrong_district.json` |

### Feedback Loop (post-visit reports)
When user reports after visiting:
- "好食" / "great" → update `verified.json` rating + add `last_visited` date
- "唔好" / "bad" → add to `blacklist.json` with reason
- "結業" / "closed" → move to `closed.json`

---

## Step 9: Weather & Seasonal Considerations

| Season/Weather | Consider |
|----------------|----------|
| 🌧️ Rainy | Indoor priority, no queuing, covered access |
| 🥵 Summer (Jun-Sep) | Air-conditioned, avoid outdoor |
| 🦀 Autumn (Sep-Nov) | Hairy crab season, snake soup |
| 🎄 Christmas/NYE | Book early, check special menus |
| 🧧 Chinese New Year | Many restaurants closed, confirm in advance |
| 🌸 Spring | Outdoor dining OK |

### Auto Weather Check (Hong Kong)
Before recommending, check weather:
```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
```
If heavy rain/typhoon → prioritize no-queue, near-MTR options.

For other cities, check local weather API or web search.

---

## JSON Schema

### verified.json
```json
{
  "last_updated": "2026-01-01",
  "restaurants": [
    {
      "name": "餐廳名",
      "name_en": "Restaurant Name",
      "district": "中環",
      "address": "Full address",
      "cuisine": "粵菜",
      "budget_pp": 300,
      "openrice_id": "r12345",
      "openrice_url": "https://www.openrice.com/zh/hongkong/r-...",
      "openrice_rating": {"food": 4.0, "ambience": 4.0, "service": 4.0, "hygiene": 4.0},
      "phone": "2XXX-XXXX",
      "nearest_mtr": "中環站 D2 出口",
      "walk_mins": 5,
      "good_for": ["商務", "慶祝"],
      "notes": "",
      "last_verified": "2026-01-01",
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
  "last_updated": "2026-01-01",
  "restaurants": []
}
```

### blacklist.json
```json
{
  "last_updated": "2026-01-01",
  "restaurants": []
}
```

### wrong_district.json
```json
{
  "last_updated": "2026-01-01",
  "corrections": []
}
```

---

## Occasion Vibe Guide

| Occasion | Keywords | Avoid |
|----------|----------|-------|
| Business lunch | Quiet, classy, good service, fast | Too noisy, street food |
| Friends hangout | Enough food, drinks, no rush, value | Too formal, overpriced |
| Celebration | Ceremony feel, upscale, photogenic | Chain fast food |
| Family / kids | Spacious, kid-friendly, baby chair | Fine dining |
| Date night | Atmosphere, lighting, privacy | Communal tables, noisy |
| Quick bite | Fast service, no queue | Needs reservation |
| Healthy | Light, organic, no MSG | Heavy flavors |

---

## Key Principles ⚠️

1. **OpenRice is the golden standard** — every recommendation must have OpenRice data
2. **Never recommend without confirming it's open** — 3-source verification, zero compromise
3. **Verify district is correct** — cross-check addresses, log errors
4. **Prices change fast** — prefer recent review pricing
5. **OpenRice link format** — `openrice.com/zh/hongkong/r-[name]-[district]-[cuisine]-r[ID]`
6. **No OpenRice record = don't recommend** — not trustworthy enough
7. **Update cache after every search** — knowledge base gets smarter over time
