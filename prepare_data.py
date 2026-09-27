#!/usr/bin/env python3
"""
prepare_data.py — Converte i dump CoinMarketCap (.txt) in oi_data.csv

Legge i 3 file data/{binance,okx,hyperliquid}.txt, estrae Open Interest
per ogni coin usando il **nome visualizzato** (CMC-normalized) come chiave
di join tra exchange, e applica il filtro "almeno 2 match".

Formato CMC atteso (blocchi di 5 righe per ogni entry):
  [Rank]
  [vuota]
  [vuota]
  [Coin Name visualizzato]  ← usato come chiave
  [Pair (es. BTC/USDT)]
  [Prezzo]
  [IndexPrice\tBasis\tVolume\tVolume%\tFunding\tOpenInterest]
"""

import csv
import re
from pathlib import Path
from collections import defaultdict, OrderedDict

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

EXCHANGE_FILES = OrderedDict([
    ("binance",     DATA / "binance.txt"),
    ("okx",         DATA / "okx.txt"),
    ("hyperliquid", DATA / "hyperliquid.txt"),
])


def parse_cmc_txt(filepath: Path) -> dict[str, dict]:
    """
    Estrae OI per nome visualizzato dal dump CoinMarketCap.

    Returns:
      {nome_normalizzato: {"base_coin": str, "oi": float}}
      dove base_coin è il ticker corto (da pair, con xyz: pulito),
      e nome_normalizzato è il nome CMC (es. "Gold (Derivatives)").
    """
    if not filepath.exists():
        return {}

    raw = filepath.read_text(encoding="utf-8")
    lines = raw.splitlines()

    results: dict[str, dict] = {}
    parsed = 0

    for i, line in enumerate(lines):
        # La riga dati ha tab separators e contiene $
        if "\t" not in line or "$" not in line:
            continue

        parts = line.split("\t")
        if len(parts) < 3:
            continue

        # OI = ultimo campo
        oi_raw = parts[-1].strip()
        oi_clean = oi_raw.replace("$", "").replace(",", "").strip()
        try:
            oi_value = float(oi_clean)
        except ValueError:
            continue

        if i < 4:
            continue

        # Risali a nome coin (3 righe sopra) e pair (2 righe sopra)
        coin_name = lines[i - 3].strip()
        pair_line = lines[i - 2].strip()

        # Skip header-like entries
        if coin_name in ("", "Currency", "Pairs", "Price", "Index Price"):
            continue

        # Estrai coin base dal pair (prima di /) e pulisci prefissi speciali
        base_coin = pair_line.split("/")[0].strip()
        # Normalizza prefissi speciali di Hyperliquid
        base_coin = re.sub(r"^xyz:", "", base_coin).strip()

        # Aggrega per nome visualizzato
        if coin_name not in results:
            results[coin_name] = {"base_coin": base_coin, "oi": 0.0}
        # AGGIUNGI SEMPRE l'OI — anche per la prima occorrenza (era 0.0)
        results[coin_name]["oi"] += oi_value

        parsed += 1

    print(f"   {filepath.name}: {parsed} pair → {len(results)} nomi univoci")
    return results


def clean_label(name: str) -> str:
    """Riduce i nomi lunghi di commodity/indici per i grafici."""
    # Rimuovi "(Derivatives)" e accorcia
    short = re.sub(r"\s*\([^)]*\)\s*", "", name).strip()
    # Se è rimasto troppo lungo, usa il base_coin
    return short


def main():
    print("=" * 60)
    print("  Prepare Data — CoinMarketCap → oi_data.csv")
    print("=" * 60)
    print()

    # 1. Parsea tutti i file
    exchange_raw: dict[str, dict[str, dict]] = {}
    for exchange, filepath in EXCHANGE_FILES.items():
        print(f"📖  Lettura {exchange}...")
        exchange_raw[exchange] = parse_cmc_txt(filepath)
        if not exchange_raw[exchange]:
            print(f"⚠️  Nessun dato per {exchange}")

    if not any(exchange_raw.values()):
        print("❌  Nessun dato trovato.")
        return

    # 2. Unione di tutti i nomi visualizzati
    all_names = set()
    for data in exchange_raw.values():
        all_names.update(data.keys())

    # 3. Costruisci righe CSV con filtro "almeno 2 match"
    rows = []
    filtered_singles = 0

    for name in sorted(all_names):
        binance_oi = exchange_raw["binance"].get(name, {}).get("oi", 0) or 0
        okx_oi     = exchange_raw["okx"].get(name, {}).get("oi", 0) or 0
        hl_oi      = exchange_raw["hyperliquid"].get(name, {}).get("oi", 0) or 0

        # Conta su quanti exchange è presente (OI > 0)
        n_present = sum(1 for v in [binance_oi, okx_oi, hl_oi] if v > 0)

        # Filtro: almeno 2 exchange
        if n_present < 2:
            filtered_singles += 1
            continue

        # Label breve: scegli il base_coin più rappresentativo
        # Ordine di preferenza: Binance > OKX > Hyperliquid
        base_coin = None
        for ex in ["binance", "okx", "hyperliquid"]:
            candidate = exchange_raw[ex].get(name, {}).get("base_coin")
            if candidate:
                base_coin = candidate
                break

        if not base_coin:
            base_coin = name

        rows.append({
            "coin":        base_coin,
            "coin_name":   name,
            "binance_oi":  binance_oi,
            "okx_oi":      okx_oi,
            "hyperliquid_oi": hl_oi,
            "n_exchanges": n_present,
        })

    rows.sort(key=lambda r: r["binance_oi"], reverse=True)

    # 4. Scrivi CSV (formato atteso da analysis.py)
    csv_path = DATA / "oi_data.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "coin", "binance_oi", "okx_oi", "hyperliquid_oi",
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "coin": r["coin"],
                "binance_oi": r["binance_oi"],
                "okx_oi": r["okx_oi"],
                "hyperliquid_oi": r["hyperliquid_oi"],
            })

    # 5. Report
    print()
    print(f"💾  Salvato {csv_path}")
    print()
    print(f"   Coin totali (almeno 2 exchange): {len(rows)}")
    print(f"   Coin filtrati (1 solo exchange):  {filtered_singles}")
    print()

    # Market share parziale (solo sui coin matchati)
    for ex in ("binance", "okx", "hyperliquid"):
        total = sum(r[f"{ex}_oi"] for r in rows)
        print(f"   {ex:12s}: OI aggregato ${total:>15,.0f}  ({len([r for r in rows if r[f'{ex}_oi'] > 0])} coin)")

    if rows:
        print()
        print("   Top 10 coin per OI Binance:")
        for r in rows[:10]:
            okx_r = r["okx_oi"] / r["binance_oi"] if r["binance_oi"] > 0 else 0
            hl_r  = r["hyperliquid_oi"] / r["binance_oi"] if r["binance_oi"] > 0 else 0
            print(f"     {r['coin']:12s}  $Bin={r['binance_oi']:>13,.0f}  "
                  f"OKX={okx_r:.2f}x  HL={hl_r:.2f}x  [{r['coin_name']}]")

    print()
    print("✅  Pronto. Ora esegui:  python analysis.py")


if __name__ == "__main__":
    main()
