from __future__ import annotations

import re
import string
from typing import Optional


PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def normalize_text(text: str) -> str:
    text = str(text).lower().strip()
    text = text.replace("\n", " ")
    text = text.translate(PUNCT_TABLE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_closed_answer(text: str) -> Optional[str]:
    norm = normalize_text(text)
    tokens = norm.split()

    if "yes" in tokens or norm.startswith("yes"):
        return "yes"
    if "no" in tokens or norm.startswith("no"):
        return "no"

    if "there is no" in norm or "there are no" in norm:
        return "no"
    if "not present" in norm or "absent" in norm:
        return "no"
    if "present" in norm:
        return "yes"

    return None


def exact_match(pred: str, gt: str) -> bool:
    return normalize_text(pred) == normalize_text(gt)


def substring_match(pred: str, gt: str) -> bool:
    pred_n = normalize_text(pred)
    gt_n = normalize_text(gt)
    return gt_n in pred_n or pred_n in gt_n


def open_match(pred: str, gt: str, mode: str = "exact") -> bool:
    if mode == "exact":
        return exact_match(pred, gt)
    if mode == "substring":
        return substring_match(pred, gt)
    raise ValueError(f"Unknown open match mode: {mode}")