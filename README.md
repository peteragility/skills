# 🛠️ OpenClaw Skills

Curated and enhanced OpenClaw agent skills — battle-tested in production.

## Skills

| Skill | Description | Files |
|-------|-------------|-------|
| [pptx](pptx/) | PowerPoint creation, editing & analysis. 18 color palettes, 5 slide types, theme system, page badges, visual QA with subagent review. | 6 |
| [xlsx](xlsx/) | Excel creation, editing & analysis. XML unpack/repack (zero format loss), formula validation & fix, OOXML cheatsheet, financial model formatting standards. | 8 |
| [fact-check](fact-check/) | Rigorous fact-checking with claim decomposition, 6-tier source reliability scoring, mandatory counter-search, logical fallacy detection, confidence scoring formula, image/video verification. | 1 |
| [find-eat](find-eat/) | Hong Kong restaurant finder with OpenRice as golden reference. 3-source verification, weather/seasonal awareness, feedback loop, verified/blacklist/closed caching. | 5 |

All skills are **portable** — no hardcoded paths, no vendor-specific tool calls, no personal data. Works with any OpenClaw agent out of the box.

## Installation

Copy the skill folder into your OpenClaw workspace skills directory:

```bash
# Install a single skill
cp -r pptx/ ~/your-workspace/skills/pptx/

# Install all skills
cp -r pptx xlsx fact-check find-eat ~/your-workspace/skills/
```

Skills use generic `web_search` instructions — compatible with any search tool (Tavily, Brave, Google, etc).

## Skill Details

### pptx (6 files)
- `SKILL.md` — Main skill instructions
- `design-system.md` — 18 professional color palettes
- `slide-types.md` — 5 slide type templates
- `pitfalls.md` — Common mistakes & fixes
- `pptxgenjs.md` — pptxgenjs API reference
- `editing.md` — Edit workflow guide

### xlsx (8 files)
- `SKILL.md` — Main skill instructions
- `create.md` / `edit.md` / `read-analyze.md` — Workflow guides
- `format.md` — Formatting standards
- `fix.md` / `validate.md` — Error handling
- `ooxml-cheatsheet.md` — OOXML XML reference

### fact-check (1 file)
- `SKILL.md` — Complete fact-checking methodology: claim decomposition, T1-T6 source tiering, confidence scoring, fallacy detection, image/video verification

### find-eat (5 files)
- `SKILL.md` — Restaurant search & verification flow
- `verified.json` / `closed.json` / `blacklist.json` / `wrong_district.json` — Cache templates (empty, populate as you use)

## Credits

- Base pptx/xlsx skills from [OpenClaw](https://github.com/openclaw/openclaw) built-in skills
- Design system, slide types, XML workflows merged from [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) (MIT)
- Fact-check and find-eat skills custom-built

## License

- `pptx` — Mixed (OpenClaw Proprietary base + MIT additions from MiniMax)
- `xlsx` — Mixed (OpenClaw Proprietary base + MIT additions from MiniMax)
- `fact-check` — MIT
- `find-eat` — MIT
