from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List

import pandas as pd


CONDITIONS = ["original", "black", "lpf", "hpf", "patch_shuffle"]


def load_summary(summary_path: str) -> Dict:
    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_summary(condition: str, summary: Dict) -> List[Dict]:
    rows: List[Dict] = []

    for group_key, group_name in [
        ("overall", "overall"),
        ("by_answer_type", "answer_type"),
        ("by_eval_mode", "eval_mode"),
        ("by_q_type", "q_type"),
        ("by_content_type", "content_type"),
        ("by_modality", "modality"),
        ("by_location", "location"),
        ("by_base_type", "base_type"),
    ]:
        if group_key == "overall":
            val = summary.get("overall", {})
            rows.append(
                {
                    "condition": condition,
                    "group": group_name,
                    "name": "overall",
                    "num_samples": val.get("num_samples"),
                    "accuracy_strict": val.get("accuracy_strict"),
                    "accuracy_relaxed": val.get("accuracy_relaxed"),
                }
            )
        else:
            for k, val in summary.get(group_key, {}).items():
                rows.append(
                    {
                        "condition": condition,
                        "group": group_name,
                        "name": k,
                        "num_samples": val.get("num_samples"),
                        "accuracy_strict": val.get("accuracy_strict"),
                        "accuracy_relaxed": val.get("accuracy_relaxed"),
                    }
                )

    return rows


def make_pivot(df: pd.DataFrame, group: str, value_col: str) -> pd.DataFrame:
    part = df[df["group"] == group].copy()
    if part.empty:
        return pd.DataFrame()

    pivot = part.pivot_table(
        index="condition",
        columns="name",
        values=value_col,
        aggfunc="first",
    )
    pivot = pivot.reindex(CONDITIONS)
    pivot = pivot.reset_index()
    return pivot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_out", type=str, default="outputs")
    parser.add_argument("--save_dir", type=str, default="outputs/compare")
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    all_rows: List[Dict] = []
    for condition in CONDITIONS:
        summary_path = os.path.join(args.base_out, condition, "summary.json")
        if not os.path.exists(summary_path):
            print(f"[WARN] Missing summary: {summary_path}")
            continue
        summary = load_summary(summary_path)
        all_rows.extend(flatten_summary(condition, summary))

    if not all_rows:
        raise FileNotFoundError("No summary.json files found.")

    df = pd.DataFrame(all_rows)
    df.to_csv(os.path.join(args.save_dir, "all_results_long.csv"), index=False)

    for group in ["overall", "answer_type", "eval_mode", "q_type", "content_type"]:
        for metric in ["accuracy_strict", "accuracy_relaxed"]:
            pivot = make_pivot(df, group, metric)
            if not pivot.empty:
                pivot.to_csv(
                    os.path.join(args.save_dir, f"{group}_{metric}_pivot.csv"),
                    index=False,
                )

    print("\nSaved comparison files to:", args.save_dir)

    overall_strict = make_pivot(df, "overall", "accuracy_strict")
    if not overall_strict.empty:
        print("\n=== overall / strict ===")
        print(overall_strict.to_string(index=False))

    overall_relaxed = make_pivot(df, "overall", "accuracy_relaxed")
    if not overall_relaxed.empty:
        print("\n=== overall / relaxed ===")
        print(overall_relaxed.to_string(index=False))


if __name__ == "__main__":
    main()