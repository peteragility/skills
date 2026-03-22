# 🛠️ OpenClaw Skills

Curated and enhanced OpenClaw agent skills — battle-tested in production.

## Skills

| Skill | Lines | Description |
|-------|-------|-------------|
| [pptx](pptx/) | 296 | PowerPoint creation, editing & analysis. 18 color palettes, 5 slide types, theme system, page badges, visual QA with subagent review. |
| [xlsx](xlsx/) | 328 | Excel creation, editing & analysis. XML unpack/repack (zero format loss), formula validation & fix, OOXML cheatsheet, financial model formatting standards. |
| [fact-check](fact-check/) | 312 | Rigorous fact-checking with claim decomposition, 6-tier source reliability scoring, mandatory counter-search, logical fallacy detection, confidence scoring formula, image/video verification. |
| [find-eat](find-eat/) | 355 | Hong Kong restaurant finder with OpenRice as golden reference. 3-source verification (OpenRice + Google + recent reviews), weather/seasonal awareness, feedback loop, verified/blacklist/closed caching. |

## Installation

Copy the skill folder into your OpenClaw workspace skills directory:

```bash
# Install a single skill
cp -r pptx/ ~/clawd/skills/pptx/

# Install all skills
cp -r pptx xlsx fact-check find-eat ~/clawd/skills/
```

## Credits

- Base pptx/xlsx/docx skills from [OpenClaw](https://github.com/openclaw/openclaw) built-in skills
- Design system, slide types, XML workflows merged from [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) (MIT)
- Fact-check and find-eat skills custom-built

## License

- `pptx` — Mixed (OpenClaw Proprietary base + MIT additions from MiniMax)
- `xlsx` — Mixed (OpenClaw Proprietary base + MIT additions from MiniMax)
- `fact-check` — MIT
- `find-eat` — MIT
