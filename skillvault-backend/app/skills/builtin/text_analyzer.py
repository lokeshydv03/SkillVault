import os
import re
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Text Analyzer Skill:
    Analyzes plain text documents or text input strings for character counts, word counts,
    sentence counts, paragraph counts, word frequencies, and keyword extraction.
    """
    file_path = input_data.get("file_path")
    text = input_data.get("text")
    user_prompt = input_data.get("input", "")

    if not file_path and not text and user_prompt:
        if "article" in user_prompt.lower():
            file_path = "sample_data/article.md"

    if file_path and os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as f:
            text = f.read()

    if not text:
        text = user_prompt

    if not text.strip():
        return {"status": "error", "message": "No text content provided."}

    # Remove markdown header tokens for plain text stats
    clean_text = re.sub(r"#+\s*", "", text)

    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
    words = [w.strip(".,!?:;\"'()[]{}*-_").lower() for w in clean_text.split() if w.strip()]

    # Word frequency analysis (filter common stop words)
    stop_words = {
        "the", "a", "an", "and", "or", "but", "is", "are", "to", "in", "of", "for", "with",
        "on", "at", "by", "from", "up", "about", "into", "through", "after", "over", "between",
        "out", "against", "during", "without", "before", "under", "around", "among", "this",
        "that", "these", "those", "it", "its", "as", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "can", "could", "should", "would", "will", "shall", "may", "might"
    }

    meaningful_words = [w for w in words if len(w) > 2 and w not in stop_words]

    freq_dict: dict[str, int] = {}
    for w in meaningful_words:
        freq_dict[w] = freq_dict.get(w, 0) + 1

    top_keywords = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "status": "success",
        "file_path": file_path or "inline_text",
        "character_count": len(text),
        "word_count": len(words),
        "unique_words": len(set(words)),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "average_words_per_sentence": (
            round(len(words) / len(sentences), 2) if sentences else 0.0
        ),
        "top_keywords": dict(top_keywords),
    }
