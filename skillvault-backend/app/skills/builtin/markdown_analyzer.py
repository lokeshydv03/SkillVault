import os
import re
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Markdown Analyzer Skill:
    Parses Markdown files, extracting document title, heading structures (H1, H2, H3),
    paragraphs, bullet lists, numbered lists, heading distribution, and word metrics.
    """
    file_path = input_data.get("file_path", "sample_data/article.md")
    text = input_data.get("markdown_text")
    user_prompt = input_data.get("input", "")

    if not text and os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as f:
            text = f.read()

    if not text and user_prompt:
        if "article" in user_prompt.lower() and os.path.exists("sample_data/article.md"):
            with open("sample_data/article.md", mode="r", encoding="utf-8") as f:
                text = f.read()

    if not text:
        return {"status": "error", "message": "No Markdown document found to analyze."}

    lines = text.splitlines()

    title = None
    headings: list[dict[str, Any]] = []
    paragraphs: list[str] = []
    bullet_list_items: list[str] = []
    numbered_list_items: list[str] = []

    heading_counts = {"h1": 0, "h2": 0, "h3": 0, "h4": 0}
    current_paragraph: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Heading detection
        heading_match = re.match(r"^(#{1,4})\s+(.+)", stripped)
        if heading_match:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []

            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            heading_tag = f"h{level}"

            if not title and level == 1:
                title = heading_text

            heading_counts[heading_tag] = heading_counts.get(heading_tag, 0) + 1
            headings.append({"level": level, "tag": heading_tag, "text": heading_text})
            continue

        # Bullet list item
        bullet_match = re.match(r"^[*+-]\s+(.+)", stripped)
        if bullet_match:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
            bullet_list_items.append(bullet_match.group(1).strip())
            continue

        # Numbered list item
        num_match = re.match(r"^\d+\.\s+(.+)", stripped)
        if num_match:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
            numbered_list_items.append(num_match.group(1).strip())
            continue

        # Blank line breaks paragraph
        if not stripped:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
        else:
            current_paragraph.append(stripped)

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    words = [w for w in text.split() if w.strip()]

    return {
        "status": "success",
        "file_path": file_path,
        "title": title or "Untitled Document",
        "total_words": len(words),
        "heading_counts": heading_counts,
        "total_headings": len(headings),
        "headings": headings,
        "total_paragraphs": len(paragraphs),
        "bullet_items_count": len(bullet_list_items),
        "numbered_items_count": len(numbered_list_items),
        "sample_bullet_items": bullet_list_items[:5],
        "sample_numbered_items": numbered_list_items[:5],
    }
