"""
Evaluación local: crea validation split y mide accuracy del pipeline.
Uso: python src/evaluate.py [--split-only] [--evaluate submission.csv]
"""

import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR


def create_validation_split(train_path: Path, val_ratio: float = 0.2, seed: int = 42):
    """Divide el training en train/val por bundles (no por filas)."""
    train_df = pd.read_csv(train_path)
    bundle_ids = train_df["bundle_asset_id"].unique()

    rng = np.random.RandomState(seed)
    rng.shuffle(bundle_ids)
    split_idx = int(len(bundle_ids) * (1 - val_ratio))

    train_bundles = set(bundle_ids[:split_idx])
    val_bundles = set(bundle_ids[split_idx:])

    train_split = train_df[train_df["bundle_asset_id"].isin(train_bundles)]
    val_split = train_df[train_df["bundle_asset_id"].isin(val_bundles)]

    train_split.to_csv(BASE_DIR / "data" / "train_split.csv", index=False)
    val_split.to_csv(BASE_DIR / "data" / "val_split.csv", index=False)

    print(f"Train split: {len(train_bundles)} bundles, {len(train_split)} pares")
    print(f"Val split: {len(val_bundles)} bundles, {len(val_split)} pares")
    return val_split


def evaluate_submission(submission_path: Path, ground_truth_path: Path):
    """Evalúa una submission contra ground truth."""
    sub_df = pd.read_csv(submission_path)
    gt_df = pd.read_csv(ground_truth_path)

    # Ground truth: bundle → set de productos
    gt_by_bundle = defaultdict(set)
    for _, row in gt_df.iterrows():
        gt_by_bundle[row["bundle_asset_id"]].add(row["product_asset_id"])

    # Submission: bundle → lista ordenada de productos (max 15)
    sub_by_bundle = defaultdict(list)
    for _, row in sub_df.iterrows():
        bid = row["bundle_asset_id"]
        if len(sub_by_bundle[bid]) < 15:
            sub_by_bundle[bid].append(row["product_asset_id"])

    # Métricas
    total_gt = 0
    total_hits = 0
    total_predicted = 0
    bundle_scores = []

    for bundle_id, gt_products in gt_by_bundle.items():
        predicted = sub_by_bundle.get(bundle_id, [])
        hits = len(set(predicted) & gt_products)
        precision = hits / len(predicted) if predicted else 0
        recall = hits / len(gt_products) if gt_products else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        bundle_scores.append({
            "bundle_id": bundle_id,
            "gt_count": len(gt_products),
            "pred_count": len(predicted),
            "hits": hits,
            "precision": precision,
            "recall": recall,
            "f1": f1
        })
        total_gt += len(gt_products)
        total_hits += hits
        total_predicted += len(predicted)

    # Métricas globales
    global_precision = total_hits / total_predicted if total_predicted else 0
    global_recall = total_hits / total_gt if total_gt else 0
    global_f1 = 2 * global_precision * global_recall / (global_precision + global_recall) if (global_precision + global_recall) > 0 else 0

    print(f"\n{'='*50}")
    print(f"RESULTADOS DE EVALUACIÓN")
    print(f"{'='*50}")
    print(f"Bundles evaluados: {len(gt_by_bundle)}")
    print(f"Total productos GT: {total_gt}")
    print(f"Total predichos: {total_predicted}")
    print(f"Aciertos: {total_hits}")
    print(f"Precision: {global_precision:.4f}")
    print(f"Recall:    {global_recall:.4f}")
    print(f"F1:        {global_f1:.4f}")
    print(f"{'='*50}")

    scores_df = pd.DataFrame(bundle_scores)
    print(f"\nMedia por bundle - Precision: {scores_df['precision'].mean():.4f}, Recall: {scores_df['recall'].mean():.4f}, F1: {scores_df['f1'].mean():.4f}")

    # Peores bundles
    worst = scores_df.nsmallest(10, "f1")
    print(f"\n10 peores bundles:")
    for _, row in worst.iterrows():
        print(f"  {row['bundle_id']}: F1={row['f1']:.3f} (GT={row['gt_count']}, pred={row['pred_count']}, hits={row['hits']})")

    return scores_df


def analyze_sections():
    """Analiza la relación entre secciones y productos."""
    bundles_df = pd.read_csv(DATA_DIR / "bundles_dataset.csv")
    train_df = pd.read_csv(DATA_DIR / "bundles_product_match_train.csv")
    products_df = pd.read_csv(DATA_DIR / "product_dataset.csv")

    bundle_sections = dict(zip(bundles_df["bundle_asset_id"], bundles_df["bundle_id_section"]))
    product_desc = dict(zip(products_df["product_asset_id"], products_df["product_description"]))

    section_products = defaultdict(set)
    section_categories = defaultdict(lambda: defaultdict(int))

    for _, row in train_df.iterrows():
        bid = row["bundle_asset_id"]
        pid = row["product_asset_id"]
        section = bundle_sections.get(bid)
        if section:
            section_products[str(section)].add(pid)
            cat = product_desc.get(pid, "UNKNOWN")
            section_categories[str(section)][cat] += 1

    print(f"\nProductos por sección (del training):")
    for section in sorted(section_products.keys()):
        print(f"  Sección {section}: {len(section_products[section])} productos únicos")

    # Guardar mapeo
    section_products_json = {k: list(v) for k, v in section_products.items()}
    with open(BASE_DIR / "embeddings" / "section_products.json", "w") as f:
        json.dump(section_products_json, f)
    print(f"Guardado section_products.json")

    # Verificar solapamiento entre secciones
    sections = list(section_products.keys())
    for i in range(len(sections)):
        for j in range(i + 1, len(sections)):
            overlap = section_products[sections[i]] & section_products[sections[j]]
            print(f"  Solapamiento sección {sections[i]} ↔ {sections[j]}: {len(overlap)} productos")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-only", action="store_true", help="Solo crear splits")
    parser.add_argument("--evaluate", type=str, help="Ruta al CSV de submission para evaluar")
    parser.add_argument("--analyze", action="store_true", help="Analizar secciones")
    args = parser.parse_args()

    (BASE_DIR / "data").mkdir(exist_ok=True)
    (BASE_DIR / "embeddings").mkdir(exist_ok=True)

    if args.split_only or not args.evaluate:
        print("Creando validation split...")
        create_validation_split(DATA_DIR / "bundles_product_match_train.csv")

    if args.analyze or not args.evaluate:
        print("\nAnalizando secciones...")
        analyze_sections()

    if args.evaluate:
        val_path = BASE_DIR / "data" / "val_split.csv"
        if not val_path.exists():
            create_validation_split(DATA_DIR / "bundles_product_match_train.csv")
        evaluate_submission(Path(args.evaluate), val_path)


if __name__ == "__main__":
    main()
