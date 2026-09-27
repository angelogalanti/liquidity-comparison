# Liquidità Exchange — Report Sintetico

**Binance vs OKX vs Hyperliquid** — Open Interest perpetual futures, dump CoinMarketCap (top 50 per volume).

**⚠️ Soglia $10M** è un'euristica pratica, non un dato scientifico. Per rigore servirebbero dati reali di spread/order book che non abbiamo. La graduatoria relativa è invece basata su dati veri.

## Crypto Asset Tradabili (esclusi sintetici)

| Exchange | ✅ Tradabili (>$10M) | ⚠️ Marginali ($5-10M) | Totale utilizzabili |
|----------|:-------------------:|:---------------------:|:-------------------:|
| **OKX** | 9 | 6 | **15** |
| **HL** | 6 | 6 | **12** |

**OKX — tradabili:** BTC, ETH, SOL, XRP, HYPE, BNB, ZEC, DOGE, NEAR
**OKX — marginali:** ADA, AAVE, LINK, LAB, RE, SLX

**HL — tradabili:** BTC, ETH, SOL, HYPE, ZEC, NEAR
**HL — marginali:** XRP, AAVE, BNB, 1000PEPE, TAO, ENA

Asset sintetici (petrolio, azioni, oro) sono esclusi da questo conteggio — vedi sezione dedicata in fondo.

## Market Share (42 coin con ≥2 exchange)

| Exchange | OI Totale | % |
|----------|-----------|:-:|
| Binance | $16.1B | 66% |
| OKX | $4.8B | 20% |
| Hyperliquid | $3.3B | 14% |

## Copertura (delle top 50 Binance)

| Exchange | Coin presenti | % |
|----------|:------------:|:-:|
| OKX | 33/37 | 89% |
| HL | 27/37 | 73% |

Mancano a OKX: WLD, TAO, 1000PEPE, ENA  
Mancano a HL: 10 coin (prevalentemente mid-small altcoin)

## Ratio Medio vs Binance

- **OKX**: media 29% (mediana 28%) — distribuzione uniforme
- **HL**: media 26% ma **mediana 17%** — distribuzione molto squilibrata (pochi coin altissimi, molti bassi)

## Soglia Liquidità per Trading

| OI | Spread stimato | Trading |
|:--:|:-------------:|:-------:|
| >$100M | <0.02% | ✅ ottimo |
| $10-100M | 0.02-0.05% | ✅ ok |
| $5-10M | 0.05-0.10% | ⚠️ marginale |
| $1-5M | 0.10-0.30% | ❌ illiquido |
| <$1M | >0.30% | ❌ non tradabile |

**Soglia pratica: ~$10M OI.** Sotto, lo spread diventa sconveniente per trading serio.

---

## ⭐ MISURAZIONE REALE order book (28/06/2026, `measure_spreads.py`)

Sostituisce la stima OI→spread con il **costo di esecuzione misurato** camminando il book (half-spread + impact reale) per un clip di $C. Round-trip = 2× one-way.

**Nomi TRADABILI (round-trip ≤ 15bps) per size del clip:**

| Size clip (AUM ~) | HL | OKX |
|---|:--:|:--:|
| **$50k (~$2M)** | **14** | **14** |
| $200k (~$8M) | 6 | 7 |
| $1M (~$40M) | 2 (BTC,ETH) | 5 (BTC,ETH,SOL,XRP,DOGE) |

**Conclusioni che CORREGGONO le soglie sopra:**
1. **La soglia $10M OI è troppo conservativa a piccola size:** misurato, a $50k/nome **entrambi i venue danno ~14 nomi** (non 6 via OI). La soglia va espressa come "depth ≥ N× il tuo clip", **non** in OI assoluto.
2. **Lo spread NON basta:** es. AVAX spread 0,2bps ma assorbe a malapena $50k; AAVE spread stretto ma book sottile. Conta la **depth**, non lo spread/OI.
3. **La soglia scala con l'AUM:** tetto di capacità del book breadth ≈ **$5-10M** (oltre, universo <10 nomi). A $40M restano 2 (HL) / 5 (OKX) nomi.
4. **HL vs OKX a $2M = pareggio (14 vs 14):** la preferenza per HL (decentralizzato) **non costa nulla** a piccola size. OKX vince solo scalando (book più profondi su BTC/ETH/major a $1M+). → **HL ora; OKX solo se >$8-10M.**
5. **Caveat:** snapshot istantanei → per una strategia lenta (posti e aspetti su 48h) sono un **lower bound**; il volume giornaliero è la metrica giusta per l'orizzonte.

⚠️ Nota: OKX richiede header browser (User-Agent) per le API pubbliche, altrimenti 403.

## Cosa è Tradabile su OKX e HL

### ✅ Trading senza problemi (OI > $10M su OKX o HL)

| Exchange | Coin |
|----------|------|
| **OKX** (14) | BTC, ETH, SOL, XRP, HYPE, BNB, ZEC, XAU, SPCX, MU, CL, DOGE, SKHYNIX, NEAR |
| **HL** (12) | BTC, ETH, SOL, HYPE, ZEC, XAU, SPCX, MU, CL, SKHYNIX, NEAR, SNDK |

### ⚠️ Marginali (OI $5-10M)

OKX: ADA, AAVE, LINK, LAB, RE, SLX  
HL: XRP, AAVE, BNB, 1000PEPE, TAO, ENA

### ❌ Troppo illiquidi (OI < $5M)

| Coin | OKX | HL | Note |
|------|:---:|:--:|------|
| O | $2.9M | — | |
| ACT | $4.7M | — | |
| AGLD | $2.2M | — | |
| ALLO | $4.2M | — | |
| RAVE | $4.3M | — | |
| S | $1.4M | $560K | entrambi sotto soglia |
| WIF | $3.9M | $1.7M | entrambi sotto soglia |
| PUMP | $11M | $22M | OK al limite su HL |

## Differenze Chiave tra OKX e HL

| Aspetto | OKX | HL |
|---------|:---:|:--:|
| Copertura | 89% (+ ampia) | 73% (- selettiva) |
| Uniformità ratio | alta (std 0.17) | bassa (std 0.38) |
| Sui propri token | BNB 12% | **HYPE 197%** |
| Asset sintetici | pochi | **forte** (CL, MU, SKHYNIX, XAU...) |
| Punto debole | assente su WLD/TAO/PEPE/ENA | debole su mid-small altcoin |

## ⚠️ Nota: Asset Sintetici su Hyperliquid

HL lista diversi **asset sintetici** (derivati su asset non-crypto) che non trovi sugli altri exchange con stessa liquidità. Riconoscerli: pair con denominazione diversa (es. `xyz:CL/USD`, `xyz:MU/USD`, `xyz:SKHX/USD`) e nomi contenenti "(Derivatives)".

Esempi presenti nell'analisi:

| Pair HL | Nome CMC | Asset Reale |
|---------|----------|-------------|
| CL (xyz:CL/USD) | Crude Oil Futures | **Petrolio greggio** |
| MU (xyz:MU/USD) | Micron Technology | **Azione Micron** |
| XAU (XAU/USD) | Gold (Derivatives) | **Oro** |
| SKHYNIX/SKHX | SK hynix Inc | **Azione SK hynix** |
| SNDK | SanDisk Corporation | **Azione SanDisk** |
| SPCX | SpaceX (Derivatives) | **SpaceX** (sintetico) |
| SAMSUNG/SMSN | Samsung Electronics | **Azione Samsung** |
| XPL (xyz:XPL/USD) | Plasma | Plasma (crypto?) |

Questi su HL hanno spesso OI paragonabile o superiore a Binance (es. **CL 0.60x**, **MU 0.64x**, **SKHYNIX 1.08x**), a differenza delle altcoin dove HL è debole.

**Implicazione pratica:** HL è un'opzione valida per tradare derivati su commodity/azioni, non solo crypto.
