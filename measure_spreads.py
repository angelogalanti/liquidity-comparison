"""
measure_spreads.py — spread e DEPTH REALI dall'order book (HL + OKX), non stime da OI.

Per ogni coin: spread top-of-book + costo EFFETTIVO per eseguire un clip di $C camminando il book
(half-spread + impact reale). Output: costo round-trip per size, e quanti nomi sono tradabili alla
NOSTRA size ($2M AUM → clip ~$50k) vs size maggiori. Risponde a "la soglia $10M OI è giusta?".
"""
import json, time, urllib.request
import numpy as np

HL = "https://api.hyperliquid.xyz/info"
OKX_BOOK = "https://www.okx.com/api/v5/market/books?instId={inst}&sz=400"
OKX_INST = "https://www.okx.com/api/v5/public/instruments?instType=SWAP"
CLIPS = [50_000, 200_000, 1_000_000]     # $ per nome: ~$2M, ~$8M, ~$40M AUM


def hl_post(body):
    req = urllib.request.Request(HL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def get(url):
    return json.load(urllib.request.urlopen(url, timeout=30))


def exec_cost(levels, mid, clip):
    """levels = [(px, notional_$_al_livello)] dal best in poi. Costo bps per riempire $clip."""
    rem, coins = clip, 0.0
    for px, notl in levels:
        if rem <= 0: break
        take = min(notl, rem); coins += take/px; rem -= take
    if rem > 1e-6 or coins <= 0: return None       # depth insufficiente
    return (clip/coins/mid - 1)*1e4


def hl_measure(coins):
    out = {}
    for c in coins:
        try:
            b = hl_post({"type": "l2Book", "coin": c})
            bids, asks = b["levels"]
            bb = float(bids[0]["px"]); ba = float(asks[0]["px"]); mid = (bb+ba)/2
            spread = (ba-bb)/mid*1e4
            lv = [(float(l["px"]), float(l["px"])*float(l["sz"])) for l in asks]
            out[c] = {"spread": spread, "mid": mid,
                      "cost": {C: exec_cost(lv, mid, C) for C in CLIPS}}
        except Exception as e:
            out[c] = {"err": str(e)[:40]}
        time.sleep(0.1)
    return out


def okx_measure(coins):
    try:
        inst = {d["instId"]: float(d["ctVal"]) for d in get(OKX_INST)["data"]}
    except Exception as e:
        print("OKX instruments err", e); return {}
    out = {}
    for c in coins:
        iid = f"{c}-USDT-SWAP"
        if iid not in inst: out[c] = {"err": "no inst"}; continue
        ctv = inst[iid]
        try:
            d = get(OKX_BOOK.format(inst=iid))["data"][0]
            bb = float(d["bids"][0][0]); ba = float(d["asks"][0][0]); mid = (bb+ba)/2
            spread = (ba-bb)/mid*1e4
            lv = [(float(p), float(p)*float(s)*ctv) for p, s, *_ in d["asks"]]
            out[c] = {"spread": spread, "mid": mid, "cost": {C: exec_cost(lv, mid, C) for C in CLIPS}}
        except Exception as e:
            out[c] = {"err": str(e)[:40]}
        time.sleep(0.15)
    return out


def fmt(v): return f"{v:>6.1f}" if v is not None else "  n/a "


def show(name, res):
    print(f"\n=== {name} — spread e costo esecuzione (bps, one-way) ===")
    print(f"  {'coin':>8} | {'spread':>6} | {'$50k':>6} {'$200k':>6} {'$1M':>6}")
    for c, r in res.items():
        if "err" in r: print(f"  {c:>8} |  {r['err']}"); continue
        cc = r["cost"]
        print(f"  {c:>8} | {r['spread']:>6.1f} | {fmt(cc[50_000])} {fmt(cc[200_000])} {fmt(cc[1_000_000])}")


def main():
    meta, ctxs = hl_post({"type": "metaAndAssetCtxs"})
    vols = sorted([(a["name"], float(c.get("dayNtlVlm", 0))) for a, c in zip(meta["universe"], ctxs)],
                  key=lambda x: -x[1])
    cand = [c for c, v in vols[:28]]
    print(f"Candidati (top 28 HL per volume): {' '.join(cand)}")

    hl = hl_measure(cand)
    okx = okx_measure([c for c in cand if c not in ("HYPE", "PUMP", "XPL", "FARTCOIN", "S")])
    show("HYPERLIQUID", hl)
    show("OKX", okx)

    # quanti nomi tradabili (round-trip = 2× one-way) sotto soglia di costo ragionevole, per size
    def tradable(res, budget_bps, clip):
        return sorted(c for c, r in res.items() if "cost" in r and r["cost"][clip] is not None and 2*r["cost"][clip] <= budget_bps)
    print("\n=== Nomi TRADABILI per size (round-trip ≤ 15bps) ===")
    for nm, res in [("HL", hl), ("OKX", okx)]:
        for C in CLIPS:
            t = tradable(res, 15, C)
            print(f"  {nm} @ ${C//1000}k/nome: {len(t):>2} nomi  {t if len(t)<=16 else t[:16]+['...']}")
    json.dump({"hl": hl, "okx": okx, "clips": CLIPS}, open("/home/x/repos/liquidity-comparison/spreads_measured.json", "w"), indent=2)
    print("\nSalvato: spreads_measured.json")


if __name__ == "__main__":
    main()
