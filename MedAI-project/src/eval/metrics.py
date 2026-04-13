from __future__ import annotations

from typing import Dict, List

import pandas as pd


def _group_summary(df: pd.DataFrame, column: str) -> Dict:
    if column not in df.columns:
        return {}

    result = {}
    for key, part in df.groupby(column):
        result[str(key)] = {
            "num_samples": int(len(part)),
            "accuracy_strict": float(part["is_correct_strict"].mean()),
            "accuracy_relaxed": float(part["is_correct_relaxed"].mean()),
        }
    return result


def build_summary(rows: List[dict]) -> Dict:
    df = pd.DataFrame(rows)
    if df.empty:
        return {
            "overall": {},
            "by_answer_type": {},
            "by_eval_mode": {},
            "by_q_type": {},
            "by_content_type": {},
            "by_modality": {},
            "by_location": {},
            "by_base_type": {},
        }

    summary = {
        "overall": {
            "num_samples": int(len(df)),
            "accuracy_strict": float(df["is_correct_strict"].mean()),
            "accuracy_relaxed": float(df["is_correct_relaxed"].mean()),
        },
        "by_answer_type": _group_summary(df, "answer_type"),
        "by_eval_mode": _group_summary(df, "eval_mode"),
        "by_q_type": _group_summary(df, "q_type"),
        "by_content_type": _group_summary(df, "content_type"),
        "by_modality": _group_summary(df, "modality"),
        "by_location": _group_summary(df, "location"),
        "by_base_type": _group_summary(df, "base_type"),
    }

    return summary