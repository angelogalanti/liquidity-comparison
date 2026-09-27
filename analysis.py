#!/usr/bin/env python3
"""
Liquidity Comparison: Binance vs OKX vs Hyperliquid
=====================================================
Analizza Open Interest (OI) dei perpetual futures per confrontare
la liquidità relativa degli exchange.

Input:  data/oi_data.csv
Output: output/*.csv, output/*.png, output/summary_stats.txt
"""

import os
import sys
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")

# ── paths ──────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "oi_data.csv"
OUT  = BASE / "output"
OUT.mkdir(parents=True, exist_ok=True)


# ── load ───────────────────────────────────────────────────────────────
def load_data(path: Path) -> pd.DataFrame:
    """Carica e valida il CSV degli OI."""
    if not path.exists():
        print(f"❌  File non trovato: {path}")
        print("   Popola data/oi_data.csv seguendo il formato in README.md")
        sys.exit(1)

    df = pd.read_csv(path)
    required = {"coin", "binance_oi", "okx_oi", "hyperliquid_oi"}
    missing = required - set(df.columns)
    if missing:
        print(f"❌  Colonne mancanti nel CSV: {missing}")
        print(f"   Colonne trovate: {list(df.columns)}")
        sys.exit(1)

    # sanity check
    assert df["coin"].notna().all(), "Coin column has NaN"
    numeric_cols = ["binance_oi", "okx_oi", "hyperliquid_oi"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    n_dropped = df[numeric_cols].isna().any(axis=1).sum()
    if n_dropped:
        print(f"⚠️  Rimosse {n_dropped} righe con OI non numerico")
        df = df.dropna(subset=numeric_cols)

    print(f"✅  Caricati {len(df)} coin da {path.name}")
    return df


# ── metrics ────────────────────────────────────────────────────────────
def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Calcola gli OI ratio rispetto a Binance."""
    ratios = df[["coin", "binance_oi", "okx_oi", "hyperliquid_oi"]].copy()
    ratios["oi_ratio_okx"]   = ratios["okx_oi"] / ratios["binance_oi"]
    ratios["oi_ratio_hl"]    = ratios["hyperliquid_oi"] / ratios["binance_oi"]
    ratios["oi_ratio_okx"]   = ratios["oi_ratio_okx"].round(4)
    ratios["oi_ratio_hl"]    = ratios["oi_ratio_hl"].round(4)

    # ordinamento per OI Binance decrescente
    ratios = ratios.sort_values("binance_oi", ascending=False).reset_index(drop=True)
    return ratios


def summary_stats(ratios: pd.DataFrame) -> str:
    """Statistiche aggregate sui ratio."""
    lines = []
    lines.append("=" * 60)
    lines.append("SUMMARY STATS — OI Ratio vs Binance")
    lines.append("=" * 60)
    lines.append("")

    # Escludi coin dove Binance = 0 (ratio infinito) dalle statistiche
    valid = ratios[ratios["binance_oi"] > 0]
    n_not_on_binance = len(ratios) - len(valid)

    for label, col in [("OKX / Binance", "oi_ratio_okx"),
                        ("Hyperliquid / Binance", "oi_ratio_hl")]:
        s = valid[col]
        lines.append(f"  {label} (solo coin su Binance):")
        lines.append(f"    Media    = {s.mean():.4f}")
        lines.append(f"    Mediana  = {s.median():.4f}")
        lines.append(f"    Min      = {s.min():.4f}")
        lines.append(f"    Max      = {s.max():.4f}")
        lines.append(f"    Std      = {s.std():.4f}")
        lines.append("")

    if n_not_on_binance:
        lines.append(f"  ⚠️  {n_not_on_binance} coin non su Binance (ratio inf) — escluse da medie sopra")
        for _, r in ratios[ratios["binance_oi"] == 0].iterrows():
            lines.append(f"      {r['coin']}: solo OKX+HL")
        lines.append("")

    # Market share
    total_binance = ratios["binance_oi"].sum()
    total_okx     = ratios["okx_oi"].sum()
    total_hl      = ratios["hyperliquid_oi"].sum()
    total_all     = total_binance + total_okx + total_hl

    lines.append("  Market share (totale OI):")
    lines.append(f"    Binance       = {total_binance:>18,.0f} USD  ({total_binance/total_all*100:.1f}%)")
    lines.append(f"    OKX           = {total_okx:>18,.0f} USD  ({total_okx/total_all*100:.1f}%)")
    lines.append(f"    Hyperliquid   = {total_hl:>18,.0f} USD  ({total_hl/total_all*100:.1f}%)")
    lines.append("")

    # Coin count by dominance threshold
    for threshold in [0.1, 0.25, 0.5, 0.75]:
        okx_count = (ratios["oi_ratio_okx"] >= threshold).sum()
        hl_count  = (ratios["oi_ratio_hl"] >= threshold).sum()
        lines.append(f"  Coin con ratio ≥ {threshold:.0%}:  OKX={okx_count:>3}  HL={hl_count:>3}")
    lines.append("")

    # Bottom / Top
    lines.append(f"  Top 3 coin per ratio OKX: {', '.join(ratios.nlargest(3, 'oi_ratio_okx')['coin'])}")
    lines.append(f"  Top 3 coin per ratio HL:  {', '.join(ratios.nlargest(3, 'oi_ratio_hl')['coin'])}")
    lines.append(f"  Bottom 3 coin per ratio OKX: {', '.join(ratios.nsmallest(3, 'oi_ratio_okx')['coin'])}")
    lines.append(f"  Bottom 3 coin per ratio HL:  {', '.join(ratios.nsmallest(3, 'oi_ratio_hl')['coin'])}")

    return "\n".join(lines)


# ── charts ─────────────────────────────────────────────────────────────
def chart_ratio_bars(ratios: pd.DataFrame, top_n: int = 30):
    """Bar chart: OI ratio per coin, Binance = 1."""
    df = ratios.head(top_n).copy()
    # Melt per Seaborn
    plot_df = df.melt(
        id_vars=["coin"],
        value_vars=["oi_ratio_okx", "oi_ratio_hl"],
        var_name="exchange",
        value_name="ratio",
    )
    plot_df["exchange"] = plot_df["exchange"].map({
        "oi_ratio_okx": "OKX",
        "oi_ratio_hl":  "Hyperliquid",
    })

    fig, ax = plt.subplots(figsize=(max(10, top_n * 0.35), 6))
    sns.barplot(
        data=plot_df, x="coin", y="ratio", hue="exchange",
        palette=["#F0B90B", "#035B5C"],
        ax=ax,
    )
    # Binance baseline
    ax.axhline(1.0, color="#1E2329", linewidth=1.2, linestyle="--", alpha=0.6, label="Binance (ref)")
    ax.set_title(f"OI Ratio vs Binance (top {top_n} coin)", fontsize=13, fontweight="bold")
    ax.set_ylabel("OI / Binance OI")
    ax.set_xlabel("")
    ax.legend(loc="upper right")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
    fig.tight_layout()
    fig.savefig(OUT / "oi_ratios_by_exchange.png", dpi=200)
    plt.close(fig)
    print(f"📊  Salvato {OUT / 'oi_ratios_by_exchange.png'}")


def chart_scatter(ratios: pd.DataFrame):
    """Scatter plot: OI OKX vs Hyperliquid, bubble = Binance OI."""
    fig, ax = plt.subplots(figsize=(8, 7))

    # bubble size (log scale)
    sizes = (ratios["binance_oi"] / ratios["binance_oi"].max() * 800) + 20

    scatter = ax.scatter(
        ratios["oi_ratio_okx"], ratios["oi_ratio_hl"],
        s=sizes, alpha=0.7, c=range(len(ratios)),
        cmap="viridis", edgecolors="white", linewidth=0.3,
    )
    ax.set_xlabel("OI Ratio OKX / Binance")
    ax.set_ylabel("OI Ratio Hyperliquid / Binance")
    ax.set_title("Confronto OI Ratio: OKX vs Hyperliquid", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.axhline(1.0, color="#1E2329", linewidth=0.8, linestyle=":", alpha=0.4)
    ax.axvline(1.0, color="#1E2329", linewidth=0.8, linestyle=":", alpha=0.4)

    # label some top coins
    top = ratios.nlargest(10, "binance_oi")
    for _, row in top.iterrows():
        ax.annotate(
            row["coin"],
            (row["oi_ratio_okx"], row["oi_ratio_hl"]),
            fontsize=7, alpha=0.8,
            xytext=(4, 4), textcoords="offset points",
        )

    fig.tight_layout()
    fig.savefig(OUT / "oi_comparison_scatter.png", dpi=200)
    plt.close(fig)
    print(f"📊  Salvato {OUT / 'oi_comparison_scatter.png'}")


def chart_ratio_distribution(ratios: pd.DataFrame):
    """Istogramma della distribuzione dei ratio."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, col, label, color in [
        (axes[0], "oi_ratio_okx", "OKX / Binance", "#F0B90B"),
        (axes[1], "oi_ratio_hl",  "Hyperliquid / Binance", "#035B5C"),
    ]:
        sns.histplot(ratios[col], bins=40, color=color, edgecolor="white", ax=ax)
        ax.axvline(ratios[col].median(), color="red", linestyle="--", linewidth=1.2,
                   label=f"mediana={ratios[col].median():.3f}")
        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_xlabel("OI Ratio")
        ax.set_ylabel("Numero coin")
        ax.legend(fontsize=9)

    fig.suptitle("Distribuzione OI Ratio rispetto a Binance", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "ratio_distribution.png", dpi=200)
    plt.close(fig)
    print(f"📊  Salvato {OUT / 'ratio_distribution.png'}")


# ── main ───────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Confronto Liquidità Exchange (OI)")
    print("  Binance · OKX · Hyperliquid")
    print("=" * 60)
    print()

    # 1. Load
    df = load_data(DATA)

    # 2. Ratios
    ratios = compute_ratios(df)

    # 3. Save CSV
    csv_path = OUT / "oi_ratios.csv"
    ratios.to_csv(csv_path, index=False)
    print(f"💾  Salvato {csv_path}  ({len(ratios)} righe)")
    print()

    # 4. Summary stats
    stats = summary_stats(ratios)
    print(stats)

    stats_path = OUT / "summary_stats.txt"
    stats_path.write_text(stats)
    print(f"💾  Salvato {stats_path}")

    # 5. Charts
    if len(ratios) >= 2:
        chart_ratio_bars(ratios, top_n=min(30, len(ratios)))
        chart_scatter(ratios)
        chart_ratio_distribution(ratios)
    else:
        print("⚠️  Meno di 2 coin — grafici saltati")

    print()
    print("✅  Analisi completata. Output in output/")


if __name__ == "__main__":
    main()
