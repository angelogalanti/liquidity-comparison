# Relazione OI ↔ Spread e Soglie LiquiditÃ  Perpetual Futures

> Ricerca multi-fonte — Giugno 2026
> Domanda: "Le nostre soglie empiriche (OI >$10M = tradabile, $5-10M = marginale, <$5M = illiquido) hanno supporto nella letteratura/pratica?"

---

## 1. OI ↔ Spread: esiste una relazione documentata?

**SÃ¬, ma solo a livello qualitativo/assunto — nessuno studio ha stimato una funzione continua OI→spread per perpetual futures.**

| Fonte | Tipo | Affermazione |
|-------|------|-------------|
| MetaMask Perps Guide | Guida trader | "Low OI can mean thinner books, wider spreads, and higher slippage risk on entries and exits." |
| CryptoFutures.trading | Guida trader | "Low open interest can indicate a lack of participation" — correlato a spread ampi. |
| Coinbase Learn | Guida exchange | "OI provides information about the liquidity and interest in a particular contract." |
| He et al. (2022) "Fundamentals of Perpetual Futures" | Paper SSRN | Bid-ask medio per perpetuals < 0.05 bps su campione Kaiko; price impact di $0.5M < 0.3 bps. Costi indiretti trascurabili vs fee dirette. **Non studia OI come predittore di spread.** |
| "Perpetual Futures & Crypto Market Quality" (SSRN 4218907) | Paper accademico | Studia l'impatto dei perps sulla qualitÃ  dello spot market. Trova che i perpetuals **allargano gli spread spot** (effetto adverse selection), ma non modella OI→spread. |
| "Two-Tiered Structure of Crypto Funding Rate Markets" (Mathematics, 2026) | Paper accademico | Usa **OI rank come proxy di liquiditÃ ** ma non calibra la relazione con spread. |

**Conclusione Q1**: La relazione OI↔spread Ã¨ universalmente *assunta* ma mai *calibrata* su dati perps. La letteratura accademica ha studiato futures-spot spread (basis) e funding rate dynamics, ma non la microstruttura OI→bid-ask spread per perpetuals. La relazione esiste ma Ã¨ indiretta (OI alto → piÃ¹ partecipazione → > book depth → spread stretti). Il proxy migliore sarebbe depth diretto, non OI.

---

## 2. Soglie pratiche: cosa usano i professionisti?

**Nessuna fonte pubblica definisce soglie OI in dollari per "liquido vs illiquido". Le uniche soglie numeriche trovate sono su depth, non OI.**

### Soglie di *depth* (Kalena.io — guida professionale 2026)

| Pair | Depth sana (0.5% dal mid) | Zona warning | Zona pericolo |
|------|--------------------------|-------------|---------------|
| BTC/USDT | >$5M | $1M–$5M | <$1M |
| ETH/USDT | >$2M | $500K–$2M | <$500K |
| Mid-cap alt | >$200K | $50K–$200K | <$50K |

Fonte: https://blog.kalena.ai/crypto-liquidity-tracker-the-6-metrics-that-separate-tradeable-markets-from-traps-and-how-to-monitor-them-in-real-time

### Soglie implicite da OI osservati su Hyperliquid (perp.wiki, 2026)

| Categoria | OI tipico | Esempi |
|-----------|-----------|--------|
| Large-cap (BTC/ETH) | $1–2B ciascuno | BTC-PERP, ETH-PERP |
| Mid-cap caldo (SOL, DOGE, PEPE) | $100M–500M+ in periodi volatili | SOL, DOGE, PEPE |
| Pair meno popolari | $5–20M | Long-tail altcoin |
| Soglia minima per esistere | ~$1–2M | Pair con pochissima attivitÃ |

Fonte: https://perp.wiki/learn/hyperliquid-open-interest-explained

### Soglie da report CoinGecko (2026)

- OI totale crypto: $99B (Aprile 2026) — giÃ¹ da picco $210B (Ottobre 2025 pre-10.10)
- Binance: ~$21B OI (dominante)
- Hyperliquid: $6-9B OI (top 5 mondiale)
- Perp DEX share OI: 13.5% (da 3.6% inizio 2025)

Fonte: https://www.coingecko.com/research/publications/state-of-crypto-perpetuals-report-2026

### Soglie da TRdesk (ranking exchange per OI)

- "Only top-5 exchanges are suitable for scalping with large volumes ($50K+ per trade)"
- OI Ã¨ considerato "un indicatore oggettivo" — volume puÃ² essere wash-traded, OI no

Fonte: https://trdesk.com/exchanges

### Soglie da Slippage-at-Risk paper (2026)

- Su 184 token Hyperliquid, il 5% tail ha solo 2.3% dell'OI totale ($196M su $8.51B)
- SaR(0.95) = slippage 2.84% — il 95% dei token ha slippage ≤ 2.84% a depth piena
- Raccomandazione: SaR aggiustato > 5% = critico, ridurre leva

Fonte: https://arxiv.org/html/2603.09164

### Proxy di liquiditÃ  da ChainCatcher (2026)

Analisi 9 exchange: rapporto OI/Volume come indicatore di "position stickiness":
- Hyperliquid: OI/Vol = 1.44 (alta ritenzione posizioni)
- OKX: OI/Vol basso (alto turnover, trading breve termine)
- MEXC: OI/Reserves = 1.96 (leva alta)

Fonte: https://www.chaincatcher.com/en/article/2264735

**Conclusione Q2**: Non esistono soglie OI assolute pubblicate da fonti autorevoli. Le nostre soglie ($10M / $5M) sono ragionevoli come *euristica*, ma andrebbero calibrate per exchange e contesto. Kalena fornisce l'unica tabella numerica pubblica — ma Ã¨ su depth, non OI.

---

## 3. Metriche alternative all'OI per liquiditÃ

| Metrica | Cosa misura | Meglio di OI? | Fonte |
|---------|------------|---------------|-------|
| **Order book depth (0.5%, 1%, 2%)** | Quanti dollari di liquidity passiva disponibile | **SÃ¬, Ã¨ la metrica diretta** | Kalena, Ostium |
| **Volume-to-OI ratio (turnover)** | Quanto velocemente il book si rigira | SÃ¬, complementare | ChainCatcher, PerpFinder |
| **Bid-ask spread (top-of-book, weighted)** | Costo immediato di entrata/uscita | SÃ¬, metrica diretta | Kalena |
| **Slippage-at-Risk (SaR)** | Slippage forward-looking da microstruttura | **SÃ¬, la piÃ¹ sofisticata** | ArXiv 2603.09164 |
| **Book imbalance ratio** | Squilibrio bid/ask entro 2% | SÃ¬, segnala direzionalitÃ  | Kalena |
| **Fill-to-cancel ratio** | Quanto della depth Ã¨ genuina | SÃ¬, filtra spoofing | Kalena |
| **OI/Reserves ratio** | SostenibilitÃ  leva dell'exchange | No (metriche exchange-level) | ChainCatcher |
| **Funding rate + OI combo** | Crowding posizionale | Complementare | Sharpe.ai, MetaMask, Thrive |

**Raccomandazione**: OI da solo non basta. Un market con $10M OI ma depth 0.5% = $50K non Ã¨ liquido. Usare depth 0.5% come metrica primaria, OI come filtro secondario.

---

## 4. Casi studio: confronti exchange via OI

| Fonte | Cosa analizza | Risultato chiave |
|-------|--------------|-----------------|
| **CoinGecko "State of Crypto Perpetuals" 2026** | OI share CEX vs DEX, trend 2025-2026 | DEX OI share 3.6% → 13.5%; Binance 33%, OKX 15% |
| **The Block** | Hyperliquid vs CEX OI mensile | Hyperliquid #5 globale per OI |
| **ChainCatcher** | 9 exchange: OI/Volume, OI/Reserves | Hyperliquid: sticky positions (OI/Vol=1.44); MEXC: alta leva (OI/Reserves=1.96) |
| **TRdesk** | Ranking real-time OI per exchange | OI come metrica anti-wash-trading |
| **PerpFinder** | OI per 30+ exchange, OI/Vol ratio per exchange | CEX dominano OI ma DEX share cresce ogni trimestre dal 2024 |

Fonte: https://www.coingecko.com/research/publications/state-of-crypto-perpetuals-report-2026
Fonte: https://chaincatcher.com/en/article/2264735
Fonte: https://trdesk.com/exchanges
Fonte: https://perpfinder.com/open-interest
Fonte: https://www.theblock.co/data/decentralized-finance/derivatives/hyperliquid-vs-exchanges-monthly-open-interest

**Nessuno ha fatto un'analisi sistematica "soglie OI → liquiditÃ  per exchange"**. Ãˆ un gap di ricerca riconosciuto.

---

## 5. Differenze per tipo di asset

| Asset class | OI tipico | LiquiditÃ  reale | Soglia OI suggerita per "liquido" |
|-------------|-----------|-----------------|----------------------------------|
| **BTC** (Binance/OKX/Hyperliquid) | $1–21B | Eccellente sub-1M, buona 1-5M, decente 5-10M | >$50M (ma depth conta piÃ¹ di OI) |
| **ETH** | $0.5–5B | Ottima | >$20M |
| **Large-cap alt (SOL, DOGE, PEPE)** | $100M–500M | Buona in periodi caldi | >$10M |
| **Mid-cap alt** | $5–50M | Variabile, spesso depth sottile | $5–10M (marginale) |
| **Small-cap / meme coin** | $1–20M | Spread ampi, slippage alto su >$10K | <$5M (illiquido) |
| **Sintetici commodity (XAU, WTI)** | <$10M (nessun exchange CEX supera $10M attivo) | Molto thin, principalmente DEX (Ostium) | <$5M di fatto |
| **Sintetici FX (USDJPY, EURUSD)** | <$5M su DEX, quasi assente su CEX | DEX-only, $134M totale OI su Ostium per RWA | <$2M |
| **Sintetici equities (AAPL, TSLA)** | $5-50M su DEX (Ostium) | Thin, 96% sintetico cash-settled | $5-10M (marginale) |

Fonti: perp.wiki, CoinMarketCap RWA Perps Report (Maggio 2026), CoinGecko 2026, Coinbase Institutional Research

**Conclusione Q5**: Le soglie cambiano drasticamente. BTC con $10M OI Ã¨ illiquido (anomalo), un altcoin con $10M OI Ã¨ nella media. Per sintetici/commodity/FX, anche $5M OI puÃ² essere considerato decente dato il mercato nascente.

---

## 6. Raccomandazione finale

### Le nostre soglie sono ragionevoli?

**SÃ¬, come euristica generica di primo filtro.** Ma con correzioni:

| Soglia attuale | Giudizio | Correzione suggerita |
|----------------|----------|---------------------|
| >$10M = tradabile | Accettabile per mid-cap su DEX/CEX medio | Per large-cap (BTC/ETH), alzare a **>$50M** |
| $5-10M = marginale | Ragionevole | Distinguere per exchange: su Binance Ã¨ molto marginale, su DEX Ã¨ la norma |
| <$5M = illiquido | Corretto per la maggior parte dei casi | Confermato: la maggior parte dei pair long-tail su Hyperliquid ha $5-20M OI |

### Aggiunte consigliate

1. **Aggiungere depth 0.5% come metrica primaria**, non solo OI. Un market con $10M OI e $50K depth non Ã¨ liquido.
2. **Calibrare per exchange**: Binance $10M ≠ Hyperliquid $10M ≠ GMX $10M. Usare ranking percentile per exchange.
3. **Aggiungere OI/Volume ratio**: se OI alto ma volume basso (ratio > 1.0), le posizioni sono sticky e il rischio di slippage improvviso aumenta (le liquidazioni colpiscono book thin).
4. **Usare soglie dinamiche**: in mercato caldo (es. BTC a $100K+), le soglie scalano con il prezzo. Ricalibrare ogni 3-6 mesi.

### Schema a 3 livelli proposto (OI + Depth combinati)

| Livello | OI | Depth 0.5% | Azione |
|---------|-----|-----------|--------|
| **Liquido** | >$10M (mid-cap) / >$50M (large-cap) | >$500K (mid) / >$5M (large) | Trading senza restrizioni |
| **Marginale** | $2-10M | $100-500K | Usare limit orders, size ridotta, monitorare spread |
| **Illiquido** | <$2M | <$100K | Evitare market orders, usare solo limit, max size $5K |

### Fonti consultate (8+)

1. MetaMask Perps Guide — https://metamask.io/news/open-interest-perps-explained
2. perp.wiki — Hyperliquid OI Explained — https://perp.wiki/learn/hyperliquid-open-interest-explained
3. Kalena.io — 6 Metrics Crypto Liquidity Tracker — https://blog.kalena.ai/crypto-liquidity-tracker-the-6-metrics-that-separate-tradeable-markets-from-traps-and-how-to-monitor-them-in-real-time
4. CoinGecko — State of Crypto Perpetuals Report 2026 — https://www.coingecko.com/research/publications/state-of-crypto-perpetuals-report-2026
5. Slippage-at-Risk (SaR) — arXiv 2603.09164 — https://arxiv.org/html/2603.09164
6. Ostium — Liquidity on Perps DEXs 2026 — https://www.ostium.com/blog/liquidity-on-perps-dexs-which-has-deepest-in-2026
7. ChainCatcher — Which exchange attracts real liquidity? — https://www.chaincatcher.com/en/article/2264735
8. TRdesk — Crypto Derivatives Exchange Rankings — https://trdesk.com/exchanges
9. He, Manela, Ross, von Wachter — "Fundamentals of Perpetual Futures" (SSRN) — https://arxiv.org/html/2212.06888v6
10. Two-Tiered Structure of Crypto Funding Rate Markets (Mathematics, 2026) — https://doi.org/10.3390/math14020346
11. CoinMarketCap — RWA Perpetuals State of the Market, May 2026
12. Coinbase Institutional — Crypto Market Positioning June 2026
13. PerpFinder — OI rankings — https://perpfinder.com/open-interest
14. Sharpe.ai — How to read OI — https://www.sharpe.ai/learn/futures-open-interest
15. VoiceOfChain — OI Short Covering Analysis — https://voiceofchain.com/academy/open-interest-analysis-short-covering
