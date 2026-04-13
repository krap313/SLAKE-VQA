# python -m src.analyze_results --base_out outputs_v3 --save_dir outputs_v3/analysis --top_k 30

from __future__ import annotations

import argparse
import os
from typing import Dict, List, Optional

import pandas as pd


DEFAULT_CONDITIONS = ["original", "black", "lpf", "hpf", "patch_shuffle"]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_predictions(base_out: str, conditions: List[str]) -> Dict[str, pd.DataFrame]:
    dfs: Dict[str, pd.DataFrame] = {}
    for condition in conditions:
        path = os.path.join(base_out, condition, "predictions.csv")
        if not os.path.exists(path):
            print(f"[WARN] Missing predictions file: {path}")
            continue

        df = pd.read_csv(path)

        # Backward compatibility
        if "is_correct_strict" not in df.columns:
            if "is_correct_exact" in df.columns:
                df["is_correct_strict"] = df["is_correct_exact"]
            elif "is_correct" in df.columns:
                df["is_correct_strict"] = df["is_correct"]
            else:
                raise ValueError(f"Could not find strict correctness column in {path}")

        if "is_correct_relaxed" not in df.columns:
            if "is_correct_substring" in df.columns:
                df["is_correct_relaxed"] = df["is_correct_substring"]
            else:
                df["is_correct_relaxed"] = df["is_correct_strict"]

        for col in [
            "answer_type",
            "eval_mode",
            "q_type",
            "content_type",
            "modality",
            "location",
            "base_type",
            "gt_answer",
            "pred_answer",
            "gt_answer_normalized",
            "pred_answer_normalized",
            "question",
            "question_id",
            "image_id",
        ]:
            if col not in df.columns:
                df[col] = "unknown"

        df["condition"] = condition
        dfs[condition] = df

    if not dfs:
        raise FileNotFoundError("No predictions.csv files were found.")
    return dfs


def metric_summary(df: pd.DataFrame, group_col: Optional[str] = None) -> pd.DataFrame:
    if group_col is None:
        return pd.DataFrame(
            [
                {
                    "num_samples": int(len(df)),
                    "accuracy_strict": float(df["is_correct_strict"].mean()),
                    "accuracy_relaxed": float(df["is_correct_relaxed"].mean()),
                }
            ]
        )

    if group_col not in df.columns:
        return pd.DataFrame()

    out = (
        df.groupby(group_col)
        .agg(
            num_samples=("question_id", "count"),
            accuracy_strict=("is_correct_strict", "mean"),
            accuracy_relaxed=("is_correct_relaxed", "mean"),
        )
        .reset_index()
        .sort_values(["num_samples", group_col], ascending=[False, True])
    )
    return out


def save_group_summaries(
    dfs: Dict[str, pd.DataFrame],
    save_dir: str,
    group_cols: List[str],
) -> None:
    rows = []
    for condition, df in dfs.items():
        overall = metric_summary(df).iloc[0].to_dict()
        rows.append(
            {
                "condition": condition,
                "group": "overall",
                "name": "overall",
                **overall,
            }
        )

        for group_col in group_cols:
            part = metric_summary(df, group_col)
            if part.empty:
                continue
            for _, row in part.iterrows():
                rows.append(
                    {
                        "condition": condition,
                        "group": group_col,
                        "name": row[group_col],
                        "num_samples": int(row["num_samples"]),
                        "accuracy_strict": float(row["accuracy_strict"]),
                        "accuracy_relaxed": float(row["accuracy_relaxed"]),
                    }
                )

    all_summary = pd.DataFrame(rows)
    all_summary.to_csv(os.path.join(save_dir, "group_summaries_long.csv"), index=False)

    for group_name in ["overall"] + group_cols:
        part = all_summary[all_summary["group"] == group_name].copy()
        if part.empty:
            continue

        for metric in ["accuracy_strict", "accuracy_relaxed"]:
            pivot = part.pivot_table(
                index="condition",
                columns="name",
                values=metric,
                aggfunc="first",
            ).reindex(DEFAULT_CONDITIONS)
            pivot.reset_index().to_csv(
                os.path.join(save_dir, f"{group_name}_{metric}_pivot.csv"),
                index=False,
            )


def save_vocab_analysis(
    dfs: Dict[str, pd.DataFrame],
    save_dir: str,
    top_k: int,
) -> None:
    for condition, df in dfs.items():
        gt_top = (
            df["gt_answer_normalized"]
            .fillna("unknown")
            .value_counts()
            .head(top_k)
            .reset_index()
        )
        gt_top.columns = ["gt_answer_normalized", "count"]
        gt_top.to_csv(
            os.path.join(save_dir, f"{condition}_top_gt_answers.csv"),
            index=False,
        )

        pred_top = (
            df["pred_answer_normalized"]
            .fillna("unknown")
            .value_counts()
            .head(top_k)
            .reset_index()
        )
        pred_top.columns = ["pred_answer_normalized", "count"]
        pred_top.to_csv(
            os.path.join(save_dir, f"{condition}_top_pred_answers.csv"),
            index=False,
        )

        wrong_only = df[~df["is_correct_strict"]].copy()
        confusion = (
            wrong_only.groupby(["gt_answer_normalized", "pred_answer_normalized"])
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(top_k)
        )
        confusion.to_csv(
            os.path.join(save_dir, f"{condition}_top_wrong_pairs.csv"),
            index=False,
        )


def save_original_baseline_errors(
    dfs: Dict[str, pd.DataFrame],
    save_dir: str,
    top_k: int,
) -> None:
    if "original" not in dfs:
        return

    df = dfs["original"].copy()

    wrong_strict = df[~df["is_correct_strict"]].copy()
    wrong_relaxed = df[~df["is_correct_relaxed"]].copy()

    wrong_strict.sort_values(["answer_type", "question_id"]).head(top_k).to_csv(
        os.path.join(save_dir, "original_wrong_examples_strict.csv"),
        index=False,
    )
    wrong_relaxed.sort_values(["answer_type", "question_id"]).head(top_k).to_csv(
        os.path.join(save_dir, "original_wrong_examples_relaxed.csv"),
        index=False,
    )

    for col in ["content_type", "modality", "location", "base_type"]:
        if col not in df.columns:
            continue
        stat = metric_summary(df, col)
        stat.to_csv(
            os.path.join(save_dir, f"original_{col}_summary.csv"),
            index=False,
        )


def merge_conditions_on_key(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    keep_cols = [
        "question_id",
        "image_id",
        "question",
        "gt_answer",
        "gt_answer_normalized",
        "answer_type",
        "eval_mode",
        "q_type",
        "content_type",
        "modality",
        "location",
        "base_type",
        "pred_answer",
        "pred_answer_normalized",
        "is_correct_strict",
        "is_correct_relaxed",
    ]

    merged = None
    for condition, df in dfs.items():
        sub = df[keep_cols].copy()
        rename_map = {
            "pred_answer": f"pred_answer__{condition}",
            "pred_answer_normalized": f"pred_answer_normalized__{condition}",
            "is_correct_strict": f"is_correct_strict__{condition}",
            "is_correct_relaxed": f"is_correct_relaxed__{condition}",
        }
        sub = sub.rename(columns=rename_map)

        if merged is None:
            merged = sub
        else:
            merged = merged.merge(
                sub,
                on=[
                    "question_id",
                    "image_id",
                    "question",
                    "gt_answer",
                    "gt_answer_normalized",
                    "answer_type",
                    "eval_mode",
                    "q_type",
                    "content_type",
                    "modality",
                    "location",
                    "base_type",
                ],
                how="inner",
            )

    if merged is None:
        raise ValueError("No data to merge.")
    return merged


def save_condition_transition_analysis(
    dfs: Dict[str, pd.DataFrame],
    save_dir: str,
    top_k: int,
) -> None:
    if "original" not in dfs:
        return

    merged = merge_conditions_on_key(dfs)
    merged.to_csv(os.path.join(save_dir, "merged_all_conditions.csv"), index=False)

    for condition in dfs.keys():
        if condition == "original":
            continue

        # original strict correct -> perturbed strict wrong
        strict_drop = merged[
            (merged["is_correct_strict__original"] == True)
            & (merged[f"is_correct_strict__{condition}"] == False)
        ].copy()
        strict_drop.to_csv(
            os.path.join(save_dir, f"original_to_{condition}_strict_drop.csv"),
            index=False,
        )

        # original relaxed correct -> perturbed relaxed wrong
        relaxed_drop = merged[
            (merged["is_correct_relaxed__original"] == True)
            & (merged[f"is_correct_relaxed__{condition}"] == False)
        ].copy()
        relaxed_drop.to_csv(
            os.path.join(save_dir, f"original_to_{condition}_relaxed_drop.csv"),
            index=False,
        )

        # original strict wrong -> perturbed strict correct
        strict_gain = merged[
            (merged["is_correct_strict__original"] == False)
            & (merged[f"is_correct_strict__{condition}"] == True)
        ].copy()
        strict_gain.to_csv(
            os.path.join(save_dir, f"original_to_{condition}_strict_gain.csv"),
            index=False,
        )

        # frequent failure categories
        for col in ["answer_type", "eval_mode", "content_type", "modality", "location", "base_type"]:
            if col not in strict_drop.columns:
                continue
            stat = (
                strict_drop.groupby(col)
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
                .head(top_k)
            )
            stat.to_csv(
                os.path.join(save_dir, f"original_to_{condition}_strict_drop_by_{col}.csv"),
                index=False,
            )


def save_prediction_bias_analysis(
    dfs: Dict[str, pd.DataFrame],
    save_dir: str,
    top_k: int,
) -> None:
    rows = []
    for condition, df in dfs.items():
        pred_counts = (
            df["pred_answer_normalized"]
            .fillna("unknown")
            .value_counts()
            .head(top_k)
            .reset_index()
        )
        pred_counts.columns = ["pred_answer_normalized", "count"]
        pred_counts["condition"] = condition
        rows.append(pred_counts)

    if rows:
        pd.concat(rows, ignore_index=True).to_csv(
            os.path.join(save_dir, "top_pred_answer_bias.csv"),
            index=False,
        )


def save_question_type_breakdown(
    dfs: Dict[str, pd.DataFrame],
    save_dir: str,
) -> None:
    rows = []
    for condition, df in dfs.items():
        for group_col in ["answer_type", "eval_mode", "content_type", "modality", "location", "base_type"]:
            if group_col not in df.columns:
                continue

            stat = metric_summary(df, group_col)
            if stat.empty:
                continue

            stat["condition"] = condition
            stat["group"] = group_col
            rows.append(stat.rename(columns={group_col: "name"}))

    if rows:
        out = pd.concat(rows, ignore_index=True)
        out.to_csv(os.path.join(save_dir, "question_type_breakdown.csv"), index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_out", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)
    parser.add_argument("--top_k", type=int, default=30)
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=DEFAULT_CONDITIONS,
    )
    args = parser.parse_args()

    ensure_dir(args.save_dir)
    dfs = load_predictions(args.base_out, args.conditions)

    group_cols = [
        "answer_type",
        "eval_mode",
        "q_type",
        "content_type",
        "modality",
        "location",
        "base_type",
    ]

    save_group_summaries(dfs, args.save_dir, group_cols)
    save_vocab_analysis(dfs, args.save_dir, args.top_k)
    save_original_baseline_errors(dfs, args.save_dir, args.top_k)
    save_condition_transition_analysis(dfs, args.save_dir, args.top_k)
    save_prediction_bias_analysis(dfs, args.save_dir, args.top_k)
    save_question_type_breakdown(dfs, args.save_dir)

    print(f"Saved analysis files to: {args.save_dir}")


if __name__ == "__main__":
    main()