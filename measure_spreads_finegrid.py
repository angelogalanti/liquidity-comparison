"""
measure_spreads_finegrid.py — stessa logica di measure_spreads.py (cammina l'order book HL),
ma con una griglia di size piu' fine ($1k-$50k) e limitata alle 11 coin del Blocco 3 del
sistema Donchian (auto-researchtrading), per stimare a quale AUM reale (trader retail,
non $2M+) ogni coin comincia ad allargarsi oltre budget.

Non sovrascrive spreads_measured.json (file esistente, popolato da Galo) — scrive un
output separato.

Uso: python3 measure_spreads_finegrid.py
"""
import json, time, urllib.request

HL = "https://api.hyperliquid.xyz/info"
CLIPS = [1_000, 2_500, 5_000, 10_000, 25_000, 50_000]
COINS = ["BTC", "ETH", "SOL", "DOGE", "ADA", "XRP", "ZEC", "BNB", "AVAX", "NEAR", "SUI"]
TAKER_RT_BPS = 9.0  # 4.5bp taker HL x2 gambe
BUDGET_BPS = 12.0


def hl_post(body):
    req = urllib.request.Request(HL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def exec_cost(levels, mid, clip):
    rem, coins = clip, 0.0
    for px, notl in levels:
        if rem <= 0: break
        take = min(notl, rem); coins += take / px; rem -= take
    if rem > 1e-6 or coins <= 0:
        return None
    return (clip / coins / mid - 1) * 1e4


def measure(coins):
    out = {}
    for c in coins:
        try:
            b = hl_post({"type": "l2Book", "coin": c})
            bids, asks = b["levels"]
            bb = float(bids[0]["px"]); ba = float(asks[0]["px"]); mid = (bb + ba) / 2
            spread = (ba - bb) / mid * 1e4
            lv = [(float(l["px"]), float(l["px"]) * float(l["sz"])) for l in asks]
            out[c] = {"spread": spread, "mid": mid,
                      "cost": {C: exec_cost(lv, mid, C) for C in CLIPS}}
        except Exception as e:
            out[c] = {"err": str(e)[:60]}
        time.sleep(0.15)
    return out


def main():
    res = measure(COINS)
    print(f"{'Coin':6} {'spread(bp)':>10}  " + "  ".join(f"${c//1000}k" for c in CLIPS))
    for c, r in res.items():
        if "err" in r:
            print(f"{c:6} err: {r['err']}"); continue
        row = f"{c:6} {r['spread']:10.2f}  "
        row += "  ".join(f"{r['cost'][C]:.1f}" if r['cost'][C] is not None else " n/a" for C in CLIPS)
        print(row)

    print(f"\nSoglia AUM stimata (budget {BUDGET_BPS}bp round-trip, fee {TAKER_RT_BPS}bp, clip=2.5% AUM):")
    for c, r in res.items():
        if "err" in r:
            continue
        last_ok_clip = None
        for C in CLIPS:
            oneway = r["cost"][C]
            if oneway is None:
                continue
            rt_total = oneway * 2 + TAKER_RT_BPS
            if rt_total <= BUDGET_BPS:
                last_ok_clip = C
        if last_ok_clip is None:
            print(f"  {c:6}: gia' sopra budget anche al clip piu' piccolo misurato (${CLIPS[0]})")
        else:
            aum = last_ok_clip / 0.025
            extra = "  (dati fermi al clip piu' alto misurato, capacita' reale puo' essere maggiore)" if last_ok_clip == CLIPS[-1] else ""
            print(f"  {c:6}: >= ${aum:,.0f} AUM (clip ${last_ok_clip:,}){extra}")

    with open("/home/x/repos/liquidity-comparison/spreads_finegrid.json", "w") as f:
        json.dump({"hl": res, "clips": CLIPS}, f, indent=2)
    print("\nSalvato: spreads_finegrid.json")


if __name__ == "__main__":
    main()
