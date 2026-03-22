# OpenClaw Skills

Curated OpenClaw agent skills — merged and enhanced from multiple sources.

## Skills

| Skill | Description |
|-------|-------------|
| [pptx](pptx/) | PowerPoint creation, editing & analysis. 18 color palettes, 5 slide types, theme system, visual QA. |
| [xlsx](xlsx/) | Excel creation, editing & analysis. XML unpack/repack, formula validation, financial formatting. |
| [fact-check](fact-check/) | Rigorous fact-checking with claim decomposition, source reliability scoring, counter-search, logical fallacy detection. |

## Installation

Copy the skill folder into your OpenClaw skills directory:

```bash
# Example: install pptx skill
cp -r pptx/ ~/clawd/skills/pptx/
```

## Credits

- Base pptx/xlsx/docx skills from OpenClaw built-in skills
- Design system, slide types, XML workflows merged from [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) (MIT)
- Fact-check skill custom-built with claim decomposition, source tiering, and counter-search methodology

## License

- `pptx` — Mixed (OpenClaw Proprietary base + MIT additions from MiniMax)
- `xlsx` — Mixed (OpenClaw Proprietary base + MIT additions from MiniMax)
- `fact-check` — MIT
