from pathlib import Path

from feishu_obsidian_local_backend.slugify import slugify_filename


def build_idea_filename(idea_text: str, ideas_dir: Path) -> str:
    slug = slugify_filename(idea_text)
    base_name = slug if slug != "capture" else "idea"
    candidate = ideas_dir / f"{base_name}.md"
    suffix = 2
    while candidate.exists():
        candidate = ideas_dir / f"{base_name}-{suffix}.md"
        suffix += 1
    return candidate.name


def render_idea_markdown(idea_text: str, source_path: Path) -> str:
    source_stem = source_path.stem
    return f"""---
type: idea
stage: exploring
audiences: []
related_themes: []
related_sources:
  - "[[01 Sources/{source_stem}]]"
validation_next_step:
---

# {idea_text}

## One-Sentence Idea

- {idea_text}

## Target User

- 

## Problem to Solve

- 

## Why Now

- 

## Borrowable Inputs

- Sources: [[01 Sources/{source_stem}]]
- Themes:

## Possible Product Shapes

- 

## Next Validation Step

- 
"""


def create_idea_note(idea_text: str, source_path: Path, ideas_dir: Path) -> Path:
    filename = build_idea_filename(idea_text, ideas_dir)
    destination = ideas_dir / filename
    destination.write_text(render_idea_markdown(idea_text, source_path), encoding="utf-8")
    return destination
