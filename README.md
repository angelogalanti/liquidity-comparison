# Liquidity Comparison — Binance vs OKX vs Hyperliquid

> **Hub Centrale**: Obsidian `comune/progetti/mega-sistema/README.md` · **Ruolo di questo repo**: Analisi e confronto della liquidità (depth/OI) Binance vs OKX vs Hyperliquid (one-off concluso).

Confronto della liquidità **perpetual futures** tra i tre exchange usando **Open Interest (OI)** come metrica primaria.

## Obiettivo

Per ogni coin, calcolare quanto sono più piccoli i mercati di OKX e Hyperliquid rispetto a Binance (baseline).

## Metrica

**Open Interest (OI)** — valore nozionale totale dei contratti aperti. Scelto perché:
- Più affidabile del volume (il volume è facilmente wash-tradabile)
- Riflette il capitale reale allocato
- Meno volatile intraday

## Input

I dati arrivano come **dump CoinMarketCap** in formato `.txt`, uno per exchange:

```
data/
├── binance.txt      ← Galo popola
├── okx.txt          ← Galo popola
└── hyperliquid.txt  ← Galo popola
```

Il formato CMC ha per ogni entry: nome coin, pair (es. BTC/USDT), prezzo, e riga dati con **Open Interest** come ultimo campo (tab-separated).

**Coppie multiple** per stesso coin (es. BTC/USDT + BTC/USDC) vengono aggregate automaticamente — l'OI totale del coin è la somma di tutti i suoi pair.

## Pipeline

```
Step 1 — Parse
  python prepare_data.py
  Legge i 3 .txt, estrae OI aggregato per coin, produce data/oi_data.csv

Step 2 — Analisi
  python analysis.py
  Legge oi_data.csv, calcola ratio e produce output/
```

## Output generati (da analysis.py)

Tutti nella cartella `output/`:

- **oi_ratios.csv** — Tabella con ratio OKX/Binance e Hyperliquid/Binance per ogni coin
- **oi_ratios_by_exchange.png** — Bar chart: OI ratio per coin, Binance normalizzato a 1
- **oi_comparison_scatter.png** — Scatter plot: OI OKX vs OI Hyperliquid (bolla = dimensione OI)
- **ratio_distribution.png** — Istogramma distribuzione dei ratio
- **summary_stats.txt** — Statistiche aggregate (media, mediana, market share, coin per soglia)

## Setup

```bash
cd ~/repos/liquidity-comparison
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
