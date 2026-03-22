---
name: fact-check
description: "Rigorous date-aware fact-checking for claims and information. Use when user asks to fact-check, verify, or validate information; check if something is true/accurate; confirm claims or statements; verify images or videos; or invokes /fact-check [claim]. Handles statistics, news events, policies, prices, scientific claims, images, and multi-language content with temporal awareness."
---

# Fact Check

## Process Overview

```
Claim → Decompose → Search (pro + counter) → Score Sources → Cross-Reference → Detect Fallacies → Verdict
```

---

## Step 1: Parse & Decompose the Claim

### Identify Claim Type

| Type | Example | Search Strategy |
|------|---------|-----------------|
| **Statistical** | "GDP grew 5%" | Official stats databases, govt sources |
| **Event** | "X happened on Y date" | News archives, multiple wire services |
| **Attribution** | "Person X said Y" | Original speech/transcript, video |
| **Comparative** | "A is bigger than B" | Both A and B data independently |
| **Causal** | "X caused Y" | Research papers, expert analysis |
| **Predictive** | "X will happen" | Expert consensus, track record |
| **Image/Video** | "This photo shows X" | Reverse image search, metadata |

### Decompose Complex Claims

Break compound claims into **atomic sub-claims** — each independently verifiable.

**Example:**
> "Tesla is the world's largest EV maker, worth more than Toyota and VW combined"

Decompose into:
1. "Tesla is the world's largest EV maker" (by what metric? units? revenue?)
2. "Tesla's market cap > Toyota's market cap + VW's market cap"

**Each sub-claim gets its own search → evidence → verdict cycle.**

---

## Step 2: Search for Evidence

### Primary Search (supporting evidence)

```
# Current facts — append current year
web_search: "[claim] [current year]"

# Specific events
web_search: "[event] [date range] official OR confirmed"

# Statistics/numbers
web_search: "[statistic] latest OR current [current year]"

# Chinese sources
web_search: "[claim in Chinese] [current year]"
```

### Counter-Search (MANDATORY — search for disconfirming evidence)

For EVERY claim, actively search for evidence that **contradicts** it:

```
# Negate the claim
web_search: "[claim] false OR debunked OR incorrect OR misleading"

# Alternative explanations
web_search: "[claim] criticism OR actually OR however"
```

**Why counter-search matters:** Confirmation bias is the #1 failure mode. If you only search for supporting evidence, you'll almost always "confirm" a claim.

### Multi-Language Strategy

| Language | Approach |
|----------|----------|
| English | Default Tavily search |
| Chinese | Search both 簡體 + 繁體 terms; check 新華社, 南華早報, 明報 |
| Mixed | Search in BOTH languages, compare narratives |

---

## Step 3: Score Source Reliability

### Source Tier System

| Tier | Reliability | Examples | Weight |
|------|-------------|----------|--------|
| **T1 — Primary** | Highest | Govt databases, company filings (SEC/HKEX), wire services (Reuters, AP, AFP), peer-reviewed journals, official transcripts | 1.0 |
| **T2 — Major Media** | High | BBC, NYT, SCMP, FT, Bloomberg, WSJ, The Economist, 明報 | 0.8 |
| **T3 — Specialist** | Medium-High | Industry publications, domain experts, reputable analysts | 0.7 |
| **T4 — General Media** | Medium | Regional news, general magazines, established blogs | 0.5 |
| **T5 — Social/User** | Low | Social media, Wikipedia (check citations), forums, personal blogs | 0.3 |
| **T6 — Known Unreliable** | Discard | Satire sites, known misinformation sources, clickbait farms | 0.0 |

### Source Red Flags (downgrade tier)

- No author or publication date
- Sensationalist headline disconnected from content
- Single anonymous source for extraordinary claim
- Site has history of corrections/retractions
- Circular sourcing (multiple articles citing each other or same single source)
- Content farm indicators (ads > content, slideshow format)

---

## Step 4: Date Verification (CRITICAL)

For EACH source, verify:

| Check | Question |
|-------|----------|
| **Source Date** | When was this published? |
| **Event Date** | When did the claimed event occur? |
| **Freshness** | Is the source recent enough? |
| **Superseded** | Has newer information replaced this? |

### Freshness Rules

| Data Type | Max Age | Notes |
|-----------|---------|-------|
| Market data (prices, market cap) | < 1 day | Changes constantly |
| Statistics / economic data | < 12 months | Check release calendar |
| People's roles / positions | < 3 months | People change jobs |
| Policies / regulations | < 6 months | Check for amendments |
| Scientific consensus | < 3 years | Unless breakthrough |
| Historical facts | No limit | Established record |

---

## Step 5: Cross-Reference & Consensus

### Minimum Source Requirements

| Claim Significance | Min Sources | Min T1/T2 Sources |
|-------------------|-------------|-------------------|
| Routine fact | 2 | 1 |
| Notable claim | 3 | 2 |
| Extraordinary claim | 5+ | 3+ |

### Consensus Analysis

- **Strong consensus** — 3+ independent T1/T2 sources agree, no credible counter-evidence
- **Weak consensus** — Sources mostly agree but with caveats or minor discrepancies
- **Disputed** — Credible sources disagree
- **No consensus** — Insufficient or contradictory evidence

---

## Step 6: Logical Fallacy Detection

Before finalizing verdict, check if the claim or evidence contains:

### Common Fallacies to Flag

| Fallacy | What It Is | Example |
|---------|-----------|---------|
| **Cherry-picking** | Selecting only favorable data | "Stock is up 200%!" (from its all-time low) |
| **Correlation ≠ Causation** | Assumes X caused Y | "Ice cream sales and drownings both rise in summer" |
| **Survivorship Bias** | Only looking at successes | "All successful founders dropped out of college" |
| **False Equivalence** | Treating unequal things as equal | "Some scientists disagree" (3 vs 10,000) |
| **Appeal to Authority** | Expert outside their domain | "Nobel physicist says vaccines are bad" |
| **Straw Man** | Misrepresenting the original claim | Debunking a version nobody actually claimed |
| **Anchoring** | First number distorts perception | "Was $1000, now only $500!" (was never worth $1000) |
| **Base Rate Neglect** | Ignoring background probability | "Test is 99% accurate" (but disease is 1 in 10,000) |
| **Misleading Framing** | True stat, deceptive presentation | "Doubled!" (from 1 to 2 out of millions) |
| **Out of Context** | Quote or data stripped of context | Partial quote changes meaning entirely |

---

## Step 7: Confidence Score Calculation

Calculate confidence systematically instead of gut feel:

```
Confidence = (Source Score + Consensus Score + Recency Score + Counter-Evidence Score) / 4
```

| Component | High (3) | Medium (2) | Low (1) |
|-----------|----------|------------|---------|
| **Source Score** | 3+ T1/T2 sources | 2 T1/T2 or 3+ T3 | Only T4/T5 sources |
| **Consensus Score** | All sources agree | Most agree, minor discrepancies | Sources contradict |
| **Recency Score** | Within freshness window | Slightly stale | Significantly outdated |
| **Counter-Evidence** | Counter-search found nothing credible | Minor counter-points | Strong counter-evidence |

| Total Score | Confidence Level |
|------------|-----------------|
| 10-12 | 🟢 **High** |
| 7-9 | 🟡 **Medium** |
| 4-6 | 🔴 **Low** |

---

## Step 8: Image / Video Fact Check

When the claim involves an image or video:

### Image Verification

1. **Reverse image search** — Use Google Lens or TinEye via browser tool
2. **Check metadata** — EXIF data (date, location, camera)
3. **Context check** — Is the image from a different event/time?
4. **Manipulation signs** — Inconsistent lighting, clone artifacts, AI generation artifacts

```bash
# Extract EXIF data
python3 -c "
from PIL import Image
from PIL.ExifTags import TAGS
img = Image.open('image.jpg')
exif = img._getexif()
if exif:
    for tag_id, value in exif.items():
        print(f'{TAGS.get(tag_id, tag_id)}: {value}')
"
```

### Video Verification

1. **Check original upload** — Find earliest version online
2. **Frame analysis** — Extract key frames, reverse search each
3. **Audio check** — Does audio match lip movement? Consistent background noise?
4. **AI detection** — Check for deepfake artifacts (unnatural blinking, edge distortion)

---

## Step 9: Report Findings

Format response as:

---

### Fact Check Result

**Claim:** [Original claim]

**Sub-claims identified:** [If decomposed, list each]

**Verdict:** [One of the following]
- ✅ **CONFIRMED** — Multiple reliable sources confirm, no credible counter-evidence
- ⚠️ **PARTIALLY TRUE** — Some aspects accurate, others not
- ❌ **FALSE** — Evidence contradicts the claim
- 🕐 **OUTDATED** — Was true but no longer accurate
- 🔀 **MISLEADING** — Technically true but framed deceptively
- ❓ **UNVERIFIABLE** — Insufficient evidence to confirm or deny

**Confidence:** [🟢 High / 🟡 Medium / 🔴 Low] (Score: X/12)

| Component | Score | Reasoning |
|-----------|-------|-----------|
| Source quality | X/3 | [brief] |
| Consensus | X/3 | [brief] |
| Recency | X/3 | [brief] |
| Counter-evidence | X/3 | [brief] |

**Date Analysis:**

| Aspect | Finding |
|--------|---------|
| Claim refers to | [date/time period] |
| Sources dated | [range] |
| Current as of | [most recent reliable date] |
| Staleness risk | [Low/Medium/High] |

**Evidence (supporting):**
1. [Source — Tier — Date] — [finding]
2. [Source — Tier — Date] — [finding]

**Counter-evidence found:**
- [Any contradicting sources or none found]

**Logical issues detected:**
- [Any fallacies flagged or "None detected"]

**Caveats:**
- [Limitations, uncertainties, context needed]

---

## Special Cases

### Fast-Changing Information
For highly dynamic data (prices, live events):
- Warn that real-time verification has limits
- Provide timestamp of your search
- Suggest official/primary sources for latest data

### Controversial / Political Topics
- Present multiple perspectives from credible sources
- Distinguish factual disputes from opinion differences
- Note if topic is politically/socially contested
- Be extra rigorous about source tier — avoid T4/T5 only

### Satire / Parody
- Check if original source is a known satire outlet (The Onion, Babylon Bee, etc.)
- Many viral claims originate from satire taken out of context

### AI-Generated Content
- Check for AI hallucination patterns (overly specific but unverifiable details)
- Look for the claim in primary sources, not just AI-generated summaries
- Flag if only source is another AI system

### No Results Found
1. Try alternative search terms (synonyms, different languages)
2. Try different time ranges
3. Check if claim is too obscure or specific
4. Report as ❓ UNVERIFIABLE with explanation
5. Suggest where user might find authoritative info
