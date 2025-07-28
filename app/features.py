from collections import Counter, defaultdict
import re
import string
from collections import Counter

def cluster_font_sizes(font_sizes, font_size_word_map, word_threshold_ratio=0.7):
    if not font_sizes or not font_size_word_map:
        return {
            "ranked_sizes": [],
            "font_counts": {},
            "body_font": None
        }

    total_words = sum(font_size_word_map.values())
    sorted_sizes = sorted(font_size_word_map.items(), key=lambda x: x[0])
    cumulative_words = 0
    body_font = None

    for size, word_count in sorted_sizes:
        cumulative_words += word_count
        if cumulative_words / total_words >= word_threshold_ratio:
            body_font = size
            break

    if not body_font:
        body_font = max(font_size_word_map.items(), key=lambda x: x[1])[0]

    return {
        "ranked_sizes": [s for s, _ in sorted(font_size_word_map.items(), key=lambda x: (-x[0], -x[1]))],
        "font_counts": dict(Counter(font_sizes)),
        "body_font": body_font
    }

def is_heading_candidate(span, font_clusters):
    text = span["text"].strip()
    size = span["size"]
    body_font = font_clusters.get("body_font", 0)
    h_candidates = font_clusters.get("h_candidates", {})

    if len(text) < 4:
        return False

    if re.match(r"^(\d+\.)+\s", text):
        return True

    in_heading_range = False
    for (low, high) in h_candidates.values():
        if low < size <= high:
            in_heading_range = True
            break

    if not in_heading_range:
        return False

    if span.get("bold"):
        return True

    if text.endswith(":") or text.isupper():
        return True

    if len(text.split()) < 15 and span.get("span_count_on_line", 1) <= 3:
        return True

    return False

def determine_numbering_level(text):
    if re.match(r"^\d+\.\d+\.\d+\s", text):
        return "H3"
    elif re.match(r"^\d+\.\d+\s", text):
        return "H2"
    elif re.match(r"^\d+\s", text):
        return "H1"
    return None


def normalize_span(span):
    return {
        "text": span.get("text", "").strip(),
        "size": round(span.get("size", 0), 1),
        "font": span.get("font", ""),
        "bold": span.get("bold", False),
        "italic": span.get("italic", False),
        "caps": span.get("caps", False),
        "page": span.get("page", 0),
        "y": round(span.get("y", 0), 1),
        "x": span.get("bbox", [0, 0, 0, 0])[0],
        "bbox": span.get("bbox", [0, 0, 0, 0]),
        "span_count_on_line": span.get("span_count_on_line", 0),
        "avg_span_width": span.get("avg_span_width", 0),
        "line_center": (span.get("bbox", [0, 0, 0, 0])[0] + span.get("bbox", [0, 0, 0, 0])[2]) / 2,
    }


import re

import re

def determine_heading_level_v2(span, body_font, avg_line_height=None, prev_span_y=None, body_x_threshold=None):
    import re

    size = span.get("size")
    x = span.get("x")
    text = span.get("text", "").strip()
    is_bold = span.get("bold", False)
    font_family = span.get("font_family", "").lower()
    span_y = span.get("y")

    if not text:
        return None

    if re.fullmatch(r"^\s*(\d+(\.\d+)*|\b(page|fig|table)\b\s*\d+(\.\d+)*)\s*$", text.lower()):
        return None

    if not any(len(w) >= 4 for w in re.findall(r'\b\w+\b', text)):
        return None

    score = 0
    font_size_score = 0
    position_score = 0
    text_pattern_score = 0
    vertical_spacing_score = 0

    if size > body_font + 2:
        font_size_score += 3
    elif size > body_font + 0.5:
        font_size_score += 2
    elif body_font - 0.5 <= size <= body_font + 0.5:
        font_size_score += 1
    else:
        return None

    if is_bold:
        score += 2

    if body_x_threshold is not None:
        if x < body_x_threshold - 10:
            position_score += 3
        elif x < body_x_threshold - 2:
            position_score += 2
        elif body_x_threshold - 2 <= x <= body_x_threshold + 5:
            position_score += 1
        else:
            position_score += 0.5
    else:
        if x < 70:
            position_score += 3
        elif x < 120:
            position_score += 2
        elif x < 200:
            position_score += 1

    words = text.split()
    word_count = len(words)

    if word_count > 12:
        return None

    if text.isupper() and len(text) > 2 and not re.fullmatch(r"^[0-9\s\W]+$", text):
        text_pattern_score += 1.5
    elif text.istitle() and len(text.split()) > 1:
        text_pattern_score += 1

    if word_count <= 7:
        text_pattern_score += 1
    elif word_count <= 15:
        text_pattern_score += 0.5

    if re.match(r"^\s*(\d+(\.\d+)*|[A-Z])[.:\-]\s+.+", text):
        text_pattern_score += 2

    if re.search(r"\b[a-zA-Z]+\s*(?:\d{2,}|\d+\.\d+)\b", text):
        return None
    punctuator_count = sum(1 for char in text if char in string.punctuation)
    if punctuator_count > 4:
        return None

    if text.endswith('.'):
        text_pattern_score -= 1
    elif text.endswith('-') or text.endswith(':'):
        text_pattern_score += 0.5

    if avg_line_height and prev_span_y and span_y:
        y_diff = span_y - prev_span_y
        if y_diff > avg_line_height * 1.8:
            vertical_spacing_score += 2
        elif y_diff > avg_line_height * 1.3:
            vertical_spacing_score += 1

    total_score = font_size_score + score + position_score + text_pattern_score + vertical_spacing_score
    
    if total_score >= 8:
        return "H1"
    elif total_score >= 4:
        return "H2"
    elif total_score >= 2.5:
        return "H3"
    return None
