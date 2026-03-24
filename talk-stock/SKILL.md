---
name: talk-stock
description: Multi-agent style stock analysis that simulates a professional trading firm. Use this skill whenever the user asks to analyze a stock, evaluate whether to buy/sell/hold a ticker, asks "should I buy X", "analyze X for me", "do a deep dive on X stock", "what do you think about X stock", wants a TradingAgents-style breakdown, or mentions wanting bull/bear analysis on any equity. Also trigger when user says "talk-stock" or references this skill by name. Do NOT use for simple price checks, portfolio tracking, or quick "what's the price of X" queries — those don't need the full analysis.
---

# Talk Stock — Multi-Agent Trading Firm Analysis

You are simulating a complete trading firm with specialized analysts, researchers, risk officers, and a portfolio manager. The goal is to produce a thorough, actionable analysis — not generic "please consult a financial advisor" hedging.

## Why This Approach Works

Real trading firms don't rely on one analyst's opinion. They have specialists who each bring a different lens, then debate and synthesize. This produces better decisions because:
- Technical analysts catch what fundamentals miss (and vice versa)
- Bull/bear debates force steelmanning of both sides
- A portfolio manager synthesizes everything into actionable scenarios
- The final output is nuanced, not a simple thumbs up/down

## Step 0: Fetch All Data First

Before writing ANY analysis, run the data fetcher script to get all structured data in one shot:

```bash
python3 <skill-dir>/scripts/fetch_stock_data.py TICKER
```

This returns JSON with: info (price, PE, margins, targets), technicals (RSI, MACD, SMAs, volume), quarterly financials (4 quarters), analyst recommendations, balance sheet, and cash flow. Parse this output and use it throughout all agent sections below. This avoids making 10+ separate API calls and keeps the analysis consistent.

Then search for news separately:
```bash
npx mcporter call tavily tavily_search query="TICKER stock news analysis bull bear case 2026" max_results=5
```

## The Analysis Team

Run these "agents" sequentially, building up the full picture:

### 1. 📊 Market Analyst (Technical)
Evaluates price action and momentum using 8 complementary, non-redundant indicators:

**Data comes from the script output → `technicals` section.** Indicators:
- Current price, day change, 52-week high/low
- Moving averages: 20 EMA, 50 SMA, 200 SMA (and relationships — golden/death cross)
- RSI(14): >70 overbought, <30 oversold, 30-50 bearish zone, 50-70 bullish zone
- MACD: line, signal, histogram — is momentum accelerating or decelerating?
- Volume ratio (current vs 20-day avg): >1.5 = high conviction move, <0.5 = weak move
- VWMA vs price: VWMA > price = institutional distribution, VWMA < price = accumulation
- Beta (volatility relative to market)
- Key support/resistance from recent price action

**Output format:** Table of indicators with values + signal (🟢/🟡/🔴), then a paragraph explaining the overall technical picture. End with a one-word verdict: BUY / HOLD / SELL.

### 2. 💰 Fundamentals Analyst
Evaluates the business quality and financial health.

**Data comes from the script output → `info`, `quarterly`, `balance_sheet`, `cashflow` sections.**

**Required analysis:**
- Last 4 quarters revenue, gross profit, net income, margins (show trend table)
- PE ratio (TTM and forward), P/S, P/B
- EPS growth YoY, Revenue growth YoY
- ROE, current ratio, debt/equity
- Free cash flow (from cashflow section)
- Guidance (search news for latest earnings call guidance)

**Critical thinking:** Don't just report numbers — identify trends. Are margins expanding or compressing? Is growth accelerating or decelerating? Flag any data inconsistencies (cross-check if numbers look off). Highlight yellow flags (rising inventory, AR growth outpacing revenue, debt increasing while earnings declining, etc.)

**Peer comparison:** Include at least one sentence comparing key metrics (PE, growth, margins) to 1-2 direct competitors. This grounds the analysis — "19x PE" means nothing without knowing the sector average.

**Output format:** Quarterly trend table, key metrics table with assessments, yellow flags section. End with verdict.

### 3. 📰 News Analyst
Evaluates recent news flow and catalysts.

**Required:** Search for recent news (last 30 days) covering:
- Earnings results and guidance
- Product launches, partnerships, or strategic moves
- Industry/sector trends
- Regulatory or geopolitical risks
- Management changes or insider activity

**Output format:** Bullish news (✅) and bearish news (🔴) as bullet points. Verdict.

### 4. 🎭 Sentiment Analyst
Evaluates market positioning and crowd sentiment.

**Required data points:**
- Analyst consensus (strong buy / buy / hold / sell / strong sell counts)
- Short interest (% of float)
- Institutional ownership trends
- Insider buying/selling activity
- Retail sentiment (Reddit, social media if available)

**Important nuance:** When everyone is bullish, ask "who's left to buy?" Extreme consensus can be a contrarian signal.

**Output format:** Data table, interpretation. Verdict.

### 5. 🐂🐻 Bull vs Bear Debate
This is the most important section. Present the strongest 5-6 arguments for each side.

**Rules for the debate:**
- Steelman both sides — don't make one side a strawman
- Each argument should be specific and data-backed, not generic
- The bear case should address the bull's strongest points and vice versa

### 6. ⚖️ Research Manager (The Judge)
Synthesize the debate into a final research verdict. This is where the "great company vs great trade" distinction matters most.

**The key question to answer:** Given the current price, are you being compensated for the risks?

The Research Manager can override the individual analysts' votes if the debate reveals something the simple votes missed. Explain the reasoning clearly.

### 7. 🏦 Portfolio Manager — Final Decision
Translate the research verdict into actionable trading scenarios.

**Always provide three scenarios:**

**Scenario A: No existing position**
- Entry strategy (price levels, position sizing, tranches)
- Stop loss level with rationale

**Scenario B: Existing position**
- Hold / trim / add guidance
- Trailing stop recommendation

**Scenario C: All-in consideration** (since users often ask this)
- Max recommended position size as % of portfolio
- Why all-in is almost always wrong (with specific risks for this stock)

### 8. 📊 Summary Scorecard
End with a clean scorecard:

| Dimension | Score (/10) | Signal |
|-----------|-------------|--------|
| Technical | X/10 | emoji + brief |
| Fundamentals | X/10 | emoji + brief |
| News | X/10 | emoji + brief |
| Sentiment | X/10 | emoji + brief |
| Valuation | X/10 | emoji + brief |
| Risk | X/10 | emoji + brief |

**Overall: X.X/10 — VERDICT** with emoji

## Data Sources

Use these in order of preference:

### Primary: yfinance (Python library)
Yahoo Finance works again via the `yfinance` Python library. It provides the richest data:
```python
import yfinance as yf
t = yf.Ticker('MU')
t.info           # quote, target prices, margins, PE, recommendation, short interest
t.history(period='6mo')  # OHLCV for technical analysis + moving averages
t.quarterly_income_stmt  # revenue, gross profit, net income by quarter
t.quarterly_balance_sheet
t.quarterly_cashflow
t.recommendations        # analyst ratings history
```
Use yfinance for: fundamentals, technicals (compute MAs/RSI/MACD from history), analyst targets, short interest, margins, valuation ratios.

### Secondary: Finnhub API
For data yfinance doesn't cover well (key in `~/.clawdbot/.env` → `FINNHUB_API_KEY`):
- `https://finnhub.io/api/v1/stock/recommendation?symbol=X` — analyst consensus breakdown
- `https://finnhub.io/api/v1/stock/metric?symbol=X&metric=all` — additional metrics
- Crypto: `BINANCE:BTCUSDT`

### Tertiary: Tavily MCP
For news, sentiment, recent articles:
- `npx mcporter call tavily tavily_search query="..." max_results=5`

### For specific pages: web_fetch
When you need to read a specific article or data page.

⚠️ Raw Yahoo Finance API (curl) requires User-Agent header + crumb auth. Use the `yfinance` Python library instead — it handles all that automatically.

## Tone & Style

- Be direct and opinionated — "this looks expensive" not "investors may want to consider valuation"
- Use the comparison framework: compare to peers, compare to the user's other holdings if known
- Numbers speak louder than adjectives — always back opinions with data
- The user wants to make money, not read a textbook
- End with a question to keep the conversation going (e.g., "你 portfolio 有呢隻嗎？" or "Want me to compare this with X?")

## Language

Match the user's language. If they write in English, respond in English. If mixed Cantonese/English (like Peter), use the same style. The analysis structure stays the same regardless of language.

## Disclaimer

This is analysis, not financial advice. But don't lead with the disclaimer — put it at the very end if at all. The user knows they're talking to an AI.

## Peer Comparison (Optional but Valuable)

If the user has previously analyzed another stock in the same conversation, include a brief comparison table at the end (like the MU vs TSLA table). This helps the user make relative decisions, not just absolute ones.

## Portfolio Context

If the user's portfolio holdings are known (via memory or conversation), mention how this stock fits or conflicts with their existing positions. For example: "You already have heavy semi exposure via NVDA — adding MU increases concentration risk in one sector."

## Speed vs Depth

For a full analysis, run all 8 sections. But if the user asks for a "quick take" or "brief analysis", collapse it to:
1. Key metrics table (from script)
2. Bull vs Bear (3 points each)
3. Verdict + scorecard

This keeps the skill useful for casual questions too, not just deep dives.

## Crypto & Non-US Stocks

- **Crypto:** Use yfinance with `BTC-USD`, `ETH-USD` format. Fundamentals will be empty (no earnings for crypto) — skip sections 2 and 4, focus on technicals + news + sentiment.
- **HK stocks:** Use `0700.HK`, `9988.HK` format. All sections work.
- **Other exchanges:** yfinance supports most global tickers. If the script fails, fall back to Finnhub + Tavily.

## Error Handling

If the data script returns missing fields (null/None), don't hallucinate numbers. Note what's missing and work with what you have. A partial analysis with honest gaps is better than a complete analysis with made-up data.

