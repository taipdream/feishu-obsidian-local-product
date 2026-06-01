import html
import re

import httpx


TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_TAG_RE = re.compile(r"<meta\s+[^>]*(?:property|name)=['\"]([^'\"]+)['\"][^>]*content=['\"]([^'\"]*)['\"][^>]*>", re.IGNORECASE)
SUPPORTED_PLATFORMS = {"generic-web", "wechat", "wechat-official-account", "xiaohongshu"}


def extract_title_from_html(document: str) -> str:
    match = TITLE_RE.search(document)
    if not match:
        return ""
    title = html.unescape(match.group(1))
    return " ".join(title.split()).strip()


def extract_meta_content(document: str, key: str) -> str:
    for name, content in META_TAG_RE.findall(document):
        if name.lower() == key.lower():
            return " ".join(html.unescape(content).split()).strip()
    return ""


def resolve_link_metadata(link: str, platform: str) -> dict:
    if not link or platform not in SUPPORTED_PLATFORMS:
        return {"resolved_title": "", "resolved_author": "", "resolved_summary": ""}

    try:
        response = httpx.get(
            link,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            },
            follow_redirects=True,
            timeout=10.0,
        )
        response.raise_for_status()
        document = response.text
        title = extract_meta_content(document, "og:title") or extract_title_from_html(document)
        author = extract_meta_content(document, "author")
        summary = extract_meta_content(document, "og:description") or extract_meta_content(document, "description")
        return {
            "resolved_title": title,
            "resolved_author": author,
            "resolved_summary": summary,
        }
    except Exception:
        return {"resolved_title": "", "resolved_author": "", "resolved_summary": ""}
