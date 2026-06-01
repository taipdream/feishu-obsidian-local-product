from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional
import re

from feishu_obsidian_local_backend.review_generator import collect_recent_notes, extract_frontmatter_lists


RELATED_LINK_RE = re.compile(r'\[\[01 Sources/([^\]]+)\]\]')
SECTION_RE = re.compile(r"^## (.+)$", re.MULTILINE)

PLAYBOOK_RULES = {
    "轻量陪伴": {
        "definition": "用低压力、连续性的支持感降低用户启动门槛，而不是一上来给重交付或重承诺。",
        "situations": [
            "用户对重承诺产品敏感，先需要一个低压力入口。",
            "适合先用内容、陪伴或轻互动建立信任。",
        ],
        "moves": [
            "先给低承诺入口，再引导到更深层互动。",
            "把支持感拆成连续触点，而不是单次说服。",
        ],
        "validation": [
            "测试低承诺入口是否能提高首次参与率。",
            "观察连续触点是否能带来更高留存或回复率。",
        ],
        "watchouts": [
            "不要只停留在安慰语气，最好给明确下一步动作。",
        ],
    },
    "情绪安慰": {
        "definition": "先承接用户情绪，再决定是否引导到行动或产品。",
        "situations": [
            "用户情绪负担高，直接推进行动会引起抗拒。",
            "适合用于焦虑、拖延或身份不稳场景的前置承接。",
        ],
        "moves": [
            "先让用户感到被理解，再进入解决方案。",
            "避免一上来强调效率、正确答案或强指导。",
        ],
        "validation": [
            "比较“先承接情绪”与“直接给建议”的互动差异。",
            "观察承接后的行动转化是否真的提升。",
        ],
        "watchouts": [
            "如果没有后续动作，纯安慰很容易变成低留存内容。",
        ],
    },
}


def _safe_note_name(label: str) -> str:
    return label.replace("/", "-").replace(":", " ").strip()


def _extract_related_context_items(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    items = []
    current = None
    capture = False
    for line in lines:
        if line.strip() == "## Related Web Context":
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if not capture or not line.strip():
            continue
        if line.startswith("- "):
            if current:
                items.append(current)
            current = {"title": line[2:].strip(), "url": "", "snippet": ""}
            continue
        if line.startswith("  - ") and current is not None:
            value = line[4:].strip()
            if value.startswith("http://") or value.startswith("https://"):
                current["url"] = value
            elif not current["snippet"]:
                current["snippet"] = value
    if current:
        items.append(current)
    return items


def _extract_section_text(path: Path, name: str) -> str:
    markdown = path.read_text(encoding="utf-8")
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip() != name:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[start:end].strip()
    return ""


def _extract_section_lines(path: Path, name: str) -> list[str]:
    section = _extract_section_text(path, name)
    if not section:
        return []
    lines = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        lines.append(line)
    return lines


def _find_related_idea_links(ideas_dir: Path, related_source_stems: set[str]) -> list[str]:
    links = []
    for path in sorted(ideas_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        linked_sources = set(RELATED_LINK_RE.findall(text))
        if linked_sources & related_source_stems:
            links.append(f'[[03 Ideas/{path.stem}]]')
    return links


def _find_related_idea_paths(ideas_dir: Path, related_source_stems: set[str]) -> list[Path]:
    paths = []
    for path in sorted(ideas_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        linked_sources = set(RELATED_LINK_RE.findall(text))
        if linked_sources & related_source_stems:
            paths.append(path)
    return paths


def _most_common(values: list[str]) -> list[tuple[str, int]]:
    counter = Counter(value for value in values if value)
    return list(counter.items())


def _source_link(path: Path) -> str:
    return f"[[01 Sources/{path.stem}]]"


def _extract_heading_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _first_unique(lines: list[str], limit: int) -> list[str]:
    seen = set()
    result = []
    for line in lines:
        normalized = line.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def _derive_playbook_sections(mechanism: str, source_paths: list[Path], related_context_items: list[dict]) -> dict:
    rule = PLAYBOOK_RULES.get(mechanism, {})
    why_lines = []
    judgment_lines = []
    for path in source_paths:
        why_lines.extend(_extract_section_lines(path, "Why I Saved This"))
        judgment_lines.extend(_extract_section_lines(path, "My Judgment"))

    situation_candidates = [
        line for line in why_lines + judgment_lines
        if any(keyword in line for keyword in ["适合", "用户", "场景", "方向", "产品", "入口"])
    ]
    situations = _first_unique(situation_candidates or (why_lines + judgment_lines), 3)

    move_candidates = [
        line for line in judgment_lines
        if not any(keyword in line for keyword in ["避免", "不要", "风险"])
    ]
    moves = _first_unique(rule.get("moves", []) + move_candidates, 4)

    validation = list(rule.get("validation", []))
    for item in related_context_items[:2]:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        if title:
            validation.append(f"补看案例：{title}")
        if snippet:
            validation.append(f"记录验证点：{snippet}")
    validation = _first_unique(validation, 4)

    watchout_candidates = [
        line for line in judgment_lines
        if any(keyword in line for keyword in ["避免", "不要", "风险"])
    ]
    watchouts = _first_unique(rule.get("watchouts", []) + watchout_candidates, 3)

    return {
        "definition": rule.get("definition", "这是一个从近期来源里抽出的候选方法模式，需要后续继续验证。"),
        "situations": situations or rule.get("situations", ["适合放在高频场景里继续观察它是否真的有效。"]),
        "moves": moves or ["从多个来源里继续总结更具体的动作。"],
        "validation": validation or ["补 2-3 条更具体的案例，再验证这个机制是否能稳定复用。"],
        "watchouts": watchouts or ["先验证这个机制是否真的带来更好的留存或转化。"],
    }


def _derive_theme_sections(theme: str, source_paths: list[Path], idea_paths: list[Path], related_context_items: list[dict]) -> dict:
    why_lines = []
    judgment_lines = []
    for path in source_paths:
        why_lines.extend(_extract_section_lines(path, "Why I Saved This"))
        judgment_lines.extend(_extract_section_lines(path, "My Judgment"))

    idea_titles = [_extract_heading_title(path) for path in idea_paths]

    definition_candidates = [
        line for line in why_lines + judgment_lines
        if theme in line or any(keyword in line for keyword in ["场景", "产品", "方向", "入口", "陪伴", "用户"])
    ]
    definition = _first_unique(definition_candidates, 1)
    definition_text = definition[0] if definition else "这是最近来源里重复出现的候选主题，适合继续观察和归档。"

    importance_candidates = _first_unique(judgment_lines + why_lines, 2)
    importance_lines = importance_candidates or ["这个主题在近期来源里重复出现，说明它可能已经不是单条灵感，而是可持续观察的方向。"]

    expression_candidates = [
        line for line in why_lines + judgment_lines
        if any(keyword in line for keyword in ["适合", "更适合", "先", "避免", "入口", "陪伴", "引导"])
    ]
    expression_lines = _first_unique(expression_candidates, 3) or ["继续从来源里补更多用户表达和内容句式。"]

    opportunity_lines = _first_unique(idea_titles + [f"可以继续观察 {theme} 是否适合沉淀成内容、社群或服务切入点。"], 3)

    question_lines = []
    if related_context_items:
        question_lines.append(f"{theme} 相关外部案例里，哪一种切入方式更容易形成稳定付费。")
    question_lines.append(f"{theme} 更适合先做内容验证，还是先做产品入口。")

    return {
        "definition": definition_text,
        "importance": importance_lines,
        "expressions": expression_lines,
        "opportunities": opportunity_lines,
        "questions": _first_unique(question_lines, 3),
    }


def _render_theme_markdown(
    theme: str,
    source_paths: list[Path],
    idea_links: list[str],
    idea_paths: list[Path],
    problems: list[tuple[str, int]],
    mechanisms: list[tuple[str, int]],
    related_context_items: list[dict],
) -> str:
    derived = _derive_theme_sections(theme, source_paths, idea_paths, related_context_items)
    related_sources = "\n".join(f'  - "{_source_link(path)}"' for path in source_paths) or "  - "
    related_ideas = "\n".join(f'  - "{link}"' for link in idea_links) or "  - "
    repeated_patterns = "\n".join(f"- {name} ({count})" for name, count in mechanisms) or "- None"
    common_problems = "\n".join(f"- {name} ({count})" for name, count in problems) or "- None"
    supporting_sources = "\n".join(f"- {_source_link(path)}" for path in source_paths) or "- None"
    supporting_ideas = "\n".join(f"- {link}" for link in idea_links) or "- None"
    why_it_matters = "\n".join(f"- {item}" for item in derived["importance"])
    common_expressions = "\n".join(f"- {item}" for item in derived["expressions"])
    opportunity_lines = "\n".join(f"- {item}" for item in derived["opportunities"])
    web_context = "\n".join(
        f"- {item['title']}\n  - {item['url']}\n  - {item['snippet']}".rstrip()
        for item in related_context_items[:5]
    ) or "- None"
    open_questions = "\n".join(f"- {item}" for item in derived["questions"])
    return f"""---
type: theme
aliases: []
related_sources:
{related_sources}
related_ideas:
{related_ideas}
---

# {theme}

## Definition

- {derived["definition"]}

## Why This Matters

{why_it_matters}

## Repeated Patterns

{repeated_patterns}

## High-Frequency Audiences

- 

## Common Problems

{common_problems}

## Common Expressions

{common_expressions}

## Potential Business Opportunities

{opportunity_lines}

## Supporting Sources

{supporting_sources}

## Related Ideas

{supporting_ideas}

## Related Web Context

{web_context}

## Open Questions

{open_questions}
"""


def _render_playbook_markdown(
    mechanism: str,
    source_paths: list[Path],
    idea_links: list[str],
    themes: list[tuple[str, int]],
    problems: list[tuple[str, int]],
    related_context_items: list[dict],
) -> str:
    derived = _derive_playbook_sections(mechanism, source_paths, related_context_items)
    definition = derived["definition"]
    situations = derived["situations"]
    moves = derived["moves"]
    validation = derived["validation"]
    watchouts = derived["watchouts"]
    related_sources = "\n".join(f'  - "{_source_link(path)}"' for path in source_paths) or "  - "
    related_ideas = "\n".join(f'  - "{link}"' for link in idea_links) or "  - "
    related_themes = "\n".join(f'  - "{name}"' for name, _ in themes) or "  - "
    theme_lines = "\n".join(f"- {name} ({count})" for name, count in themes) or "- None"
    problem_lines = "\n".join(f"- {name} ({count})" for name, count in problems) or "- None"
    situation_lines = "\n".join(f"- {item}" for item in situations)
    move_lines = "\n".join(f"- {item}" for item in moves)
    validation_lines = "\n".join(f"- {item}" for item in validation)
    watchout_lines = "\n".join(f"- {item}" for item in watchouts)
    source_lines = "\n".join(f"- {_source_link(path)}" for path in source_paths) or "- None"
    idea_lines = "\n".join(f"- {link}" for link in idea_links) or "- None"
    web_context = "\n".join(
        f"- {item['title']}\n  - {item['url']}\n  - {item['snippet']}".rstrip()
        for item in related_context_items[:5]
    ) or "- None"
    return f"""---
type: playbook
status: draft
derived_from_mechanism: {mechanism}
related_themes:
{related_themes}
related_sources:
{related_sources}
related_ideas:
{related_ideas}
---

# {mechanism}

## Core Mechanism

- {definition}

## Best-Fit Situations

{situation_lines}

## Repeated Theme Signals

{theme_lines}

## Repeated Problem Signals

{problem_lines}

## Draft Moves

{move_lines}

## Validation Moves

{validation_lines}

## Watchouts

{watchout_lines}

## Supporting Sources

{source_lines}

## Related Ideas

{idea_lines}

## Related Web Context

{web_context}
"""


def create_pattern_notes(
    sources_dir: Path,
    ideas_dir: Path,
    themes_dir: Path,
    playbooks_dir: Path,
    now: Optional[datetime] = None,
    days: int = 7,
    min_count: int = 2,
) -> dict:
    now = now or datetime.now()
    themes_dir.mkdir(parents=True, exist_ok=True)
    playbooks_dir.mkdir(parents=True, exist_ok=True)

    recent_sources = [
        note
        for note in collect_recent_notes(sources_dir, days=days, now=now)
        if not note["path"].stem.startswith("example-")
    ]
    source_values = {}
    for note in recent_sources:
        source_values[note["path"]] = extract_frontmatter_lists(note["path"])

    theme_counter = Counter()
    mechanism_counter = Counter()
    for values in source_values.values():
        theme_counter.update(values["themes"])
        mechanism_counter.update(values["mechanisms"])

    created_themes = []
    created_playbooks = []

    for theme, count in theme_counter.items():
        if count < min_count:
            continue
        related_paths = [path for path, values in source_values.items() if theme in values["themes"]]
        related_source_stems = {path.stem for path in related_paths}
        idea_links = _find_related_idea_links(ideas_dir, related_source_stems)
        idea_paths = _find_related_idea_paths(ideas_dir, related_source_stems)
        problems = _most_common([problem for path in related_paths for problem in source_values[path]["problems"]])
        mechanisms = _most_common([mechanism for path in related_paths for mechanism in source_values[path]["mechanisms"]])
        related_context_items = []
        seen_urls = set()
        for path in related_paths:
            for item in _extract_related_context_items(path):
                url = item.get("url", "")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                related_context_items.append(item)
        destination = themes_dir / f"{_safe_note_name(theme)}.md"
        destination.write_text(
            _render_theme_markdown(theme, related_paths, idea_links, idea_paths, problems, mechanisms, related_context_items),
            encoding="utf-8",
        )
        created_themes.append(destination)

    for mechanism, count in mechanism_counter.items():
        if count < min_count:
            continue
        related_paths = [path for path, values in source_values.items() if mechanism in values["mechanisms"]]
        related_source_stems = {path.stem for path in related_paths}
        idea_links = _find_related_idea_links(ideas_dir, related_source_stems)
        themes = _most_common([theme for path in related_paths for theme in source_values[path]["themes"]])
        problems = _most_common([problem for path in related_paths for problem in source_values[path]["problems"]])
        related_context_items = []
        seen_urls = set()
        for path in related_paths:
            for item in _extract_related_context_items(path):
                url = item.get("url", "")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                related_context_items.append(item)
        destination = playbooks_dir / f"{_safe_note_name(mechanism)}.md"
        destination.write_text(
            _render_playbook_markdown(mechanism, related_paths, idea_links, themes, problems, related_context_items),
            encoding="utf-8",
        )
        created_playbooks.append(destination)

    return {
        "themes": created_themes,
        "playbooks": created_playbooks,
    }
