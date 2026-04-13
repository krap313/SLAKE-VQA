from __future__ import annotations

import argparse
import os
from typing import Dict, List

from tqdm import tqdm

from src.data.slake_dataset import SlakeDataset
from src.eval.metrics import build_summary
from src.eval.parsing import (
    exact_match,
    normalize_text,
    parse_closed_answer,
    substring_match,
)
from src.models.huatuo_qwen import HuatuoQwenVLM
from src.transforms.image_conditions import get_condition_fn
from src.utils.io import ensure_dir, save_csv, save_json, save_jsonl
from src.utils.logger import setup_logger
from src.utils.seed import set_seed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        type=str,
        default="FreedomIntelligence/HuatuoGPT-Vision-7B-Qwen2.5VL",
    )
    parser.add_argument("--slake_root", type=str, default=None)
    parser.add_argument("--use_hf", action="store_true")
    parser.add_argument("--hf_dataset_name", type=str, default="BoKelvin/SLAKE")
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument(
        "--condition",
        type=str,
        default="original",
        choices=["original", "black", "lpf", "hpf", "patch_shuffle"],
    )
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--max_samples", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lpf_sigma", type=float, default=3.0)
    parser.add_argument("--hpf_sigma", type=float, default=3.0)
    parser.add_argument("--patch_size", type=int, default=16)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--max_new_tokens", type=int, default=16)
    return parser.parse_args()


def is_yes_no_answer(text: str) -> bool:
    norm = normalize_text(text)
    return norm in {"yes", "no"}


def main():
    args = parse_args()
    ensure_dir(args.output_dir)
    logger = setup_logger(args.output_dir)
    set_seed(args.seed)

    if not args.use_hf and args.slake_root is None:
        raise ValueError("When --use_hf is not set, --slake_root must be provided.")

    dataset = SlakeDataset(
        slake_root=args.slake_root,
        split=args.split,
        english_only=True,
        use_hf=args.use_hf,
        hf_dataset_name=args.hf_dataset_name,
    )

    if args.max_samples is not None:
        dataset.samples = dataset.samples[: args.max_samples]

    logger.info("Loaded %d samples", len(dataset))
    model = HuatuoQwenVLM(model_name=args.model_name, device=args.device)
    condition_fn = get_condition_fn(args.condition)

    rows: List[Dict] = []

    for idx in tqdm(range(len(dataset)), desc=f"Evaluating-{args.condition}"):
        sample = dataset[idx]
        try:
            image = sample["image"]

            if args.condition == "lpf":
                image = condition_fn(image, sigma=args.lpf_sigma)
            elif args.condition == "hpf":
                image = condition_fn(image, sigma=args.hpf_sigma)
            elif args.condition == "patch_shuffle":
                image = condition_fn(image, patch_size=args.patch_size, seed=args.seed)
            else:
                image = condition_fn(image)

            pred_raw = model.generate_answer(
                image=image,
                question=sample["question"],
                max_new_tokens=args.max_new_tokens,
            )

            gt_answer_raw = sample["answer"]

            if is_yes_no_answer(gt_answer_raw):
                gt_norm = parse_closed_answer(gt_answer_raw)
                pred_norm = parse_closed_answer(pred_raw)

                is_correct_strict = (gt_norm is not None) and (pred_norm == gt_norm)
                is_correct_relaxed = is_correct_strict
                eval_mode = "yes_no"

                gt_eval = gt_norm if gt_norm is not None else normalize_text(gt_answer_raw)
                pred_eval = pred_norm if pred_norm is not None else normalize_text(pred_raw)
            else:
                gt_eval = normalize_text(gt_answer_raw)
                pred_eval = normalize_text(pred_raw)

                is_correct_strict = exact_match(pred_raw, gt_answer_raw)
                is_correct_relaxed = substring_match(pred_raw, gt_answer_raw)
                eval_mode = "text_match"

            rows.append(
                {
                    "image_id": sample["image_id"],
                    "question_id": sample["question_id"],
                    "question": sample["question"],
                    "gt_answer": sample["answer"],
                    "pred_answer": pred_raw,
                    "gt_answer_normalized": gt_eval,
                    "pred_answer_normalized": pred_eval,
                    "answer_type": sample["answer_type"],
                    "q_type": sample["q_type"],
                    "content_type": sample.get("content_type", "unknown"),
                    "modality": sample.get("modality", "unknown"),
                    "location": sample.get("location", "unknown"),
                    "base_type": sample.get("base_type", "unknown"),
                    "condition": args.condition,
                    "eval_mode": eval_mode,
                    "is_correct_strict": bool(is_correct_strict),
                    "is_correct_relaxed": bool(is_correct_relaxed),
                }
            )

        except Exception as exc:
            logger.exception(
                "Failed on sample idx=%d question_id=%s: %s",
                idx,
                sample.get("question_id"),
                exc,
            )

    summary = build_summary(rows)
    summary["meta"] = {
        "model_name": args.model_name,
        "split": args.split,
        "condition": args.condition,
        "seed": args.seed,
        "num_predictions": len(rows),
        "lpf_sigma": args.lpf_sigma,
        "hpf_sigma": args.hpf_sigma,
        "patch_size": args.patch_size,
        "use_hf": args.use_hf,
        "hf_dataset_name": args.hf_dataset_name,
        "slake_root": args.slake_root,
    }

    save_jsonl(rows, os.path.join(args.output_dir, "predictions.jsonl"))
    save_csv(rows, os.path.join(args.output_dir, "predictions.csv"))
    save_json(summary, os.path.join(args.output_dir, "summary.json"))

    flat_rows = [{"group": "overall", "name": "overall", **summary["overall"]}]
    for group_name in [
        "by_answer_type",
        "by_eval_mode",
        "by_q_type",
        "by_content_type",
        "by_modality",
        "by_location",
        "by_base_type",
    ]:
        for k, v in summary.get(group_name, {}).items():
            flat_rows.append(
                {
                    "group": group_name.replace("by_", ""),
                    "name": k,
                    **v,
                }
            )

    save_csv(flat_rows, os.path.join(args.output_dir, "summary.csv"))

    logger.info("Finished. Results saved to %s", args.output_dir)
    logger.info(
        "Overall strict accuracy: %.4f",
        summary.get("overall", {}).get("accuracy_strict", 0.0),
    )
    logger.info(
        "Overall relaxed accuracy: %.4f",
        summary.get("overall", {}).get("accuracy_relaxed", 0.0),
    )


if __name__ == "__main__":
    main()