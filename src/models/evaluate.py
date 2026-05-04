"""Model evaluation helpers."""

from __future__ import annotations

import pandas as pd


def binary_classification_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    """Compute simple dependency-free binary classification metrics."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")

    tp = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 1 and pred == 1)
    tn = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 0 and pred == 0)
    fp = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 0 and pred == 1)
    fn = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 1 and pred == 0)
    total = len(y_true)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": precision,
        "sensitivity": recall,
        "specificity": specificity,
        "f1": f1,
        "tp": float(tp),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
    }


def subgroup_event_rates(df: pd.DataFrame, group_col: str, target_col: str) -> pd.DataFrame:
    """Return event rates by subgroup for quick bias/error review."""
    if group_col not in df.columns or target_col not in df.columns:
        raise ValueError("group and target columns must exist")
    return (
        df.groupby(group_col, dropna=False)[target_col]
        .agg(["count", "mean"])
        .rename(columns={"mean": "event_rate"})
        .reset_index()
    )
