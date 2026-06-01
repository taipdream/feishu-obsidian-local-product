from datetime import datetime
from pathlib import Path
from typing import Optional
import re

from feishu_obsidian_local_backend.related_context import maybe_collect_related_context, tavily_search


TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}")
QUESTION_SUFFIX_RE = re.compile(
    r"(的?(运营团队)?(优势|特点|问题|机会|差异|能力|模式)(在|是)?哪里|"
    r"我该不该|怎么|如何|为什么|有没有|帮我分析|给我建议|"
    r"是什么|有哪些|是什么样的|呢|吗|么|\?|？)+$"
)


def _latest_file(directory: Path, pattern: str) -> Optional[Path]:
    files = sorted(directory.glob(pattern))
    return files[-1] if files else None


def tokenize(text: str) -> list[str]:
    tokens = []
    for token in TOKEN_RE.findall(text):
        lowered = token.lower()
        tokens.append(lowered)
        if re.fullmatch(r"[\u4e00-\u9fff]{2,}", token):
            for index in range(len(token) - 1):
                tokens.append(token[index : index + 2].lower())
    return tokens


def build_collection_suggestions(question: str) -> list[str]:
    tokens = tokenize(question)
    subject = tokens[0] if tokens else "该对象"
    return [
        f"补 1-3 条直接相关来源，至少覆盖 {subject} 的团队介绍或官方资料。",
        f"补 1-2 条关于 {subject} 运营动作、内容案例或产品页面的观察记录。",
        f"补 1-2 条你自己的判断笔记，说明你为什么会问这个问题，以及你怀疑它的优势可能来自哪里。",
    ]


def build_web_fallback_query(question: str) -> str:
    normalized = question.strip()
    normalized = normalized.rstrip("？?。！! ")
    core = QUESTION_SUFFIX_RE.sub("", normalized).strip()
    core = core.replace("的", " ").strip()
    core = re.sub(r"\s+", " ", core)
    if not core:
        core = normalized
    return f"{core} 官网 团队 运营 介绍 案例"


def _extract_section_lines(path: Optional[Path], marker: str) -> list[str]:
    if path is None or not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    collected = []
    capture = False
    for line in lines:
        if line.strip() == marker:
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture and line.strip():
            collected.append(line)
    return collected


def _note_link(path: Path, link_prefix: str) -> str:
    return f"[[{link_prefix}/{path.stem}]]"


def _section_score(lines: list[str], question_tokens: set[str], weight: int) -> int:
    if not lines or not question_tokens:
        return 0
    text = "\n".join(lines)
    note_tokens = tokenize(text)
    return sum(weight for token in note_tokens if token in question_tokens)


def score_note(question: str, path: Path, note_type: str) -> int:
    question_tokens = set(tokenize(question))
    if not question_tokens:
        return 0

    title = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    score = 0
    score += _section_score([title], question_tokens, 5)

    weighted_sections = {
        "source": ["## Why I Saved This", "## My Judgment", "## Related Web Context"],
        "idea": ["## One-Sentence Idea", "## Problem to Solve", "## Borrowable Inputs"],
        "theme": ["## Definition", "## Why This Matters", "## Common Expressions", "## Potential Business Opportunities"],
        "playbook": ["## Core Mechanism", "## Best-Fit Situations", "## Draft Moves", "## Validation Moves"],
    }

    for marker in weighted_sections.get(note_type, []):
        weight = 4 if marker in {"## Definition", "## Core Mechanism", "## One-Sentence Idea", "## Why I Saved This", "## My Judgment"} else 2
        score += _section_score(_extract_section_lines(path, marker), question_tokens, weight)

    whole_text_score = _section_score([path.read_text(encoding="utf-8")], question_tokens, 1)
    score += whole_text_score
    return score


def collect_ranked_notes(
    question: str,
    directory: Optional[Path],
    note_type: str,
    link_prefix: str,
    limit: int = 3,
    related_texts: Optional[list[str]] = None,
) -> list[dict]:
    if directory is None or not directory.exists():
        return []
    related_tokens = set(tokenize("\n".join(related_texts or [])))
    scored = []
    for path in sorted(directory.glob("*.md")):
        score = score_note(question, path, note_type)
        if score == 0 and related_tokens:
            score = _section_score([path.read_text(encoding="utf-8")], related_tokens, 1)
        if score > 0:
            scored.append(
                {
                    "score": score,
                    "path": path,
                    "note_type": note_type,
                    "link": _note_link(path, link_prefix),
                }
            )
    scored.sort(key=lambda item: (-item["score"], item["path"].name))
    return scored[:limit]


def collect_relevant_context_snippets(notes: list[dict]) -> list[str]:
    snippets = []
    for note in notes:
        for marker in [
            "## Why I Saved This",
            "## My Judgment",
            "## Definition",
            "## Core Mechanism",
            "## Related Web Context",
        ]:
            section_lines = _extract_section_lines(note["path"], marker)
            if section_lines:
                snippets.extend(section_lines[:2])
    unique = []
    seen = set()
    for line in snippets:
        normalized = line.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
        if len(unique) >= 8:
            break
    return unique


def render_answer_markdown(
    question: str,
    context_summary: str,
    review_path: Optional[Path],
    opportunity_path: Optional[Path],
    direct_notes: list[dict],
    signal_notes: list[dict],
    context_snippets: list[str],
    web_fallback_items: list[dict],
) -> str:
    pattern_lines = _extract_section_lines(review_path, "## Pattern Signals")
    direction_lines = _extract_section_lines(opportunity_path, "## Direction 1")
    pattern_text = "\n".join(pattern_lines) if pattern_lines else "- None"
    direction_text = "\n".join(direction_lines) if direction_lines else "- None"

    direct_evidence_text = "\n".join(f"- {note['link']}" for note in direct_notes)
    if context_snippets:
        direct_evidence_text = (direct_evidence_text + "\n" if direct_evidence_text else "") + "\n".join(f"- {line}" for line in context_snippets)
    if not direct_evidence_text:
        direct_evidence_text = "- 库内证据不足，当前回答不能直接判断具体对象。"

    signal_text = "\n".join(f"- {note['link']}" for note in signal_notes) or "- None"
    web_fallback_text = "\n".join(
        f"- {item['title']}\n  - {item['url']}\n  - {item['snippet']}".rstrip()
        for item in web_fallback_items
    ) or "- None"

    current_read = (
        "- 当前本地资料更支持把这个问题理解为“先判断有没有直接证据，再用相关主题和方法做旁证”。"
        if direct_notes
        else "- 当前本地资料不足以直接回答这个对象问题，只能先给出有限的相关信号和外部参考。"
    )
    inference = (
        "- 根据本地直接证据，这个问题已经有初步判断基础，但仍然需要继续验证是否只是单条观察。"
        if direct_notes
        else "- 目前只能把外部结果当成参考，不能当成已经进入你资料库的确认结论。"
    )
    suggestion_lines = "\n".join(f"- {line}" for line in build_collection_suggestions(question)) if not direct_notes else "- None"

    return f"""# Answer - {question}

## Question

- {question}

## Conversation Context

{context_summary or "- None"}

## Direct Evidence

{direct_evidence_text}

## Related Signals

{signal_text}

## Supporting Signals

{pattern_text}

## Current Read

{current_read}

## Inference

{inference}

## Web Fallback

{web_fallback_text}

## Suggested Collection Next

{suggestion_lines}

## Best Current Direction

{direction_text}

## Next Move

- Pick one direction only.
- Run 3 user conversations before expanding scope.
"""


def build_answer_chat_reply(
    direct_notes: list[dict],
    signal_notes: list[dict],
    web_fallback_items: list[dict],
) -> str:
    if direct_notes:
        source_count = len(direct_notes)
        signal_count = len(signal_notes)
        return (
            f"当前判断：本地库里已经有 {source_count} 条直接证据"
            f"{'，并且还有 ' + str(signal_count) + ' 条相关信号' if signal_count else ''}。\n"
            "建议先按这些本地材料继续判断，再决定是否补更多对象资料。"
        )
    if web_fallback_items:
        first = web_fallback_items[0].get("title", "外部结果")
        return (
            "当前判断：本地库里还没有直接证据。\n"
            f"我先补了外部参考，当前最接近的是：{first}。\n"
            "建议尽快补 1-3 条这个对象的本地来源。"
        )
    return "当前判断：本地库里还没有足够证据，建议先补 1-3 条直接相关来源。"


def build_answer_result(
    question: str,
    reviews_dir: Path,
    sources_dir: Optional[Path] = None,
    ideas_dir: Optional[Path] = None,
    themes_dir: Optional[Path] = None,
    playbooks_dir: Optional[Path] = None,
    tavily_api_key: str = "",
    web_search_fn=tavily_search,
    analysis_question: Optional[str] = None,
    context_summary: str = "",
) -> Path:
    analysis_text = analysis_question or question
    review_path = _latest_file(reviews_dir, "review-*.md")
    opportunity_path = _latest_file(reviews_dir, "opportunities-*.md")

    source_notes = collect_ranked_notes(analysis_text, sources_dir, "source", "01 Sources")
    idea_notes = collect_ranked_notes(analysis_text, ideas_dir, "idea", "03 Ideas")
    direct_notes = source_notes + idea_notes
    direct_texts = [note["path"].read_text(encoding="utf-8") for note in direct_notes]
    theme_notes = collect_ranked_notes(analysis_text, themes_dir, "theme", "02 Themes", related_texts=direct_texts)
    playbook_notes = collect_ranked_notes(analysis_text, playbooks_dir, "playbook", "04 Playbooks", related_texts=direct_texts)
    signal_notes = theme_notes + playbook_notes
    context_snippets = collect_relevant_context_snippets(direct_notes + signal_notes)

    web_fallback_items = []
    if not direct_notes:
        web_fallback_items = maybe_collect_related_context(
            build_web_fallback_query(analysis_text),
            tavily_api_key,
            web_search_fn,
        )

    markdown = render_answer_markdown(
        question,
        context_summary,
        review_path,
        opportunity_path,
        direct_notes,
        signal_notes,
        context_snippets,
        web_fallback_items,
    )
    return {
        "markdown": markdown,
        "direct_notes": direct_notes,
        "signal_notes": signal_notes,
        "web_fallback_items": web_fallback_items,
    }


def create_answer_note(
    question: str,
    reviews_dir: Path,
    answers_dir: Path,
    now: Optional[datetime] = None,
    sources_dir: Optional[Path] = None,
    ideas_dir: Optional[Path] = None,
    themes_dir: Optional[Path] = None,
    playbooks_dir: Optional[Path] = None,
    tavily_api_key: str = "",
    web_search_fn=tavily_search,
    analysis_question: Optional[str] = None,
    context_summary: str = "",
) -> Path:
    now = now or datetime.now()
    result = build_answer_result(
        question,
        reviews_dir,
        sources_dir=sources_dir,
        ideas_dir=ideas_dir,
        themes_dir=themes_dir,
        playbooks_dir=playbooks_dir,
        tavily_api_key=tavily_api_key,
        web_search_fn=web_search_fn,
        analysis_question=analysis_question,
        context_summary=context_summary,
    )

    answers_dir.mkdir(parents=True, exist_ok=True)
    destination = answers_dir / f"answer-{now.strftime('%Y-%m-%d-%H%M%S')}.md"
    destination.write_text(result["markdown"], encoding="utf-8")
    return destination
