# python -m src.make_report --analysis_dir outputs_v3/analysis --output_path outputs_v3/analysis/report.md

from __future__ import annotations

import argparse
import os
from typing import List

import pandas as pd


def read_csv_if_exists(path: str) -> pd.DataFrame | None:
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def df_to_md(df: pd.DataFrame, max_rows: int = 10) -> str:
    if df is None or df.empty:
        return "_No data available._"
    return df.head(max_rows).to_markdown(index=False)


def pick_pivot_row(df: pd.DataFrame, condition: str = "original") -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    if "condition" not in df.columns:
        return df.head(1)
    part = df[df["condition"] == condition]
    if part.empty:
        return df.head(1)
    return part


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis_dir", type=str, required=True)
    parser.add_argument("--output_path", type=str, default=None)
    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    output_path = args.output_path or os.path.join(analysis_dir, "report.md")

    overall_strict = read_csv_if_exists(os.path.join(analysis_dir, "overall_accuracy_strict_pivot.csv"))
    overall_relaxed = read_csv_if_exists(os.path.join(analysis_dir, "overall_accuracy_relaxed_pivot.csv"))
    answer_type_strict = read_csv_if_exists(os.path.join(analysis_dir, "answer_type_accuracy_strict_pivot.csv"))
    answer_type_relaxed = read_csv_if_exists(os.path.join(analysis_dir, "answer_type_accuracy_relaxed_pivot.csv"))
    bias_df = read_csv_if_exists(os.path.join(analysis_dir, "top_pred_answer_bias.csv"))
    wrong_pairs_original = read_csv_if_exists(os.path.join(analysis_dir, "original_top_wrong_pairs.csv"))
    wrong_examples_original = read_csv_if_exists(os.path.join(analysis_dir, "original_wrong_examples_strict.csv"))
    drop_black = read_csv_if_exists(os.path.join(analysis_dir, "original_to_black_strict_drop_by_answer_type.csv"))
    drop_patch = read_csv_if_exists(os.path.join(analysis_dir, "original_to_patch_shuffle_strict_drop_by_answer_type.csv"))
    drop_hpf = read_csv_if_exists(os.path.join(analysis_dir, "original_to_hpf_strict_drop_by_answer_type.csv"))

    lines: List[str] = []
    lines.append("# SLAKE 이미지 의존성 분석 리포트")
    lines.append("")
    lines.append("이 문서는 `src.analyze_results`가 생성한 분석 결과를 바탕으로 자동 생성된 요약 리포트입니다.")
    lines.append("")

    lines.append("## 1. Overall Accuracy (Strict)")
    lines.append("")
    lines.append(df_to_md(overall_strict, max_rows=10))
    lines.append("")

    lines.append("## 2. Overall Accuracy (Relaxed)")
    lines.append("")
    lines.append(df_to_md(overall_relaxed, max_rows=10))
    lines.append("")

    lines.append("## 3. Answer Type Accuracy (Strict)")
    lines.append("")
    lines.append(df_to_md(answer_type_strict, max_rows=10))
    lines.append("")

    lines.append("## 4. Answer Type Accuracy (Relaxed)")
    lines.append("")
    lines.append(df_to_md(answer_type_relaxed, max_rows=10))
    lines.append("")

    lines.append("## 5. 자주 생성되는 예측 답변")
    lines.append("")
    lines.append(df_to_md(bias_df, max_rows=20))
    lines.append("")

    lines.append("## 6. Original 조건에서 자주 발생하는 오답 쌍")
    lines.append("")
    lines.append(df_to_md(wrong_pairs_original, max_rows=20))
    lines.append("")

    lines.append("## 7. Original 조건에서의 대표 오답 예시")
    lines.append("")
    lines.append(df_to_md(wrong_examples_original, max_rows=20))
    lines.append("")

    lines.append("## 8. Original 대비 Black에서 성능이 떨어진 샘플 분포")
    lines.append("")
    lines.append(df_to_md(drop_black, max_rows=20))
    lines.append("")

    lines.append("## 9. Original 대비 Patch Shuffle에서 성능이 떨어진 샘플 분포")
    lines.append("")
    lines.append(df_to_md(drop_patch, max_rows=20))
    lines.append("")

    lines.append("## 10. Original 대비 HPF에서 성능이 떨어진 샘플 분포")
    lines.append("")
    lines.append(df_to_md(drop_hpf, max_rows=20))
    lines.append("")

    lines.append("## 11. 해석 가이드")
    lines.append("")
    lines.append("- `strict`는 exact match 기준이므로 보수적인 지표다.")
    lines.append("- `relaxed`는 substring 기준이므로 의미적으로 부분적으로 맞는 답을 일부 허용한다.")
    lines.append("- `black`에서 큰 성능 하락이 없으면 텍스트 prior 의존 가능성을 의심할 수 있다.")
    lines.append("- `patch_shuffle`에서 성능 하락이 크면 spatial structure 활용 가능성이 있다.")
    lines.append("- `open`의 낮은 점수는 모델 자체 한계와 채점 기준의 엄격함이 함께 반영된 결과일 수 있다.")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Saved report to: {output_path}")


if __name__ == "__main__":
    main()