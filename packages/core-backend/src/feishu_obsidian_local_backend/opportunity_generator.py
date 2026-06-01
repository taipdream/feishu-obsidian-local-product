from datetime import datetime
from pathlib import Path
from typing import Optional
import re


SIGNAL_LINE_RE = re.compile(r"^- (Themes|Problems|Mechanisms):\s*(.*)$", re.MULTILINE)
PAIR_RE = re.compile(r"(.+?)\s+\((\d+)\)")


def parse_review_signals(markdown: str) -> dict:
    bucket_map = {
        "Themes": "themes",
        "Problems": "problems",
        "Mechanisms": "mechanisms",
    }
    result = {"themes": [], "problems": [], "mechanisms": []}
    for match in SIGNAL_LINE_RE.finditer(markdown):
        bucket = bucket_map[match.group(1)]
        raw = match.group(2).strip()
        if raw == "None":
            continue
        pairs = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            pair_match = PAIR_RE.match(chunk)
            if not pair_match:
                continue
            pairs.append((pair_match.group(1).strip(), int(pair_match.group(2))))
        result[bucket] = pairs
    return result


def find_latest_review(reviews_dir: Path) -> Optional[Path]:
    reviews = sorted(reviews_dir.glob("review-*.md"))
    return reviews[-1] if reviews else None


def collect_idea_links(ideas_dir: Path) -> list[str]:
    return [f"[[03 Ideas/{path.stem}]]" for path in sorted(ideas_dir.glob("*.md"))]


def collect_review_source_links(review_path: Path) -> list[str]:
    lines = review_path.read_text(encoding="utf-8").splitlines()
    collected = []
    capture = False
    for line in lines:
        if line.strip() == "## Sources":
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture and line.strip().startswith("- [[01 Sources/"):
            collected.append(line.strip()[2:])
    return collected


def build_directions(signals: dict) -> list[dict]:
    themes = [name for name, _ in signals["themes"]] or ["待观察主题"]
    problems = [name for name, _ in signals["problems"]] or ["待观察问题"]
    mechanisms = [name for name, _ in signals["mechanisms"]] or ["待观察机制"]
    directions = []
    for index in range(3):
        theme = themes[index % len(themes)]
        problem = problems[index % len(problems)]
        mechanism = mechanisms[index % len(mechanisms)]
        directions.append(
            {
                "title": f"{theme} x {problem}",
                "thesis": f"围绕 {theme} 场景下的 {problem}，用 {mechanism} 做更低门槛的切入。",
                "next_step": f"访谈 3 位出现 {problem} 的目标用户，验证她们是否会被 {mechanism} 这类方案吸引。",
            }
        )
    return directions


def render_opportunity_brief(now: datetime, signals: dict, idea_links: list[str], source_links: list[str]) -> str:
    directions = build_directions(signals)
    related_ideas = "\n".join(f"- {link}" for link in idea_links) or "- None"
    related_sources = "\n".join(f"- {link}" for link in source_links) or "- None"
    sections = []
    for index, direction in enumerate(directions, start=1):
        sections.append(
            f"""## Direction {index}

- Focus: {direction['title']}
- Thesis: {direction['thesis']}
- Next step: {direction['next_step']}
"""
        )
    body = "\n".join(sections)
    return f"""# Opportunity Brief - {now.date().isoformat()}

## Inputs

- Related ideas:
{related_ideas}
- Related sources:
{related_sources}

## Opportunity Directions

{body}
"""


def create_opportunity_brief(
    reviews_dir: Path,
    ideas_dir: Path,
    output_dir: Path,
    now: Optional[datetime] = None,
) -> Path:
    now = now or datetime.now()
    latest_review = find_latest_review(reviews_dir)
    if latest_review is None:
        raise FileNotFoundError("No review files found")
    signals = parse_review_signals(latest_review.read_text(encoding="utf-8"))
    idea_links = collect_idea_links(ideas_dir)
    source_links = collect_review_source_links(latest_review)
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"opportunities-{now.date().isoformat()}.md"
    destination.write_text(render_opportunity_brief(now, signals, idea_links, source_links), encoding="utf-8")
    return destination
