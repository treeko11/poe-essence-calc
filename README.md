# PoE Essence Upgrade Calculator

**Live:** https://treeko11.github.io/poe-essence-calc/

A Path of Exile tool that uses poe.ninja prices to tell you whether to sell your
Screaming and Shrieking essences as they are, or vendor them 3-for-1 up to the next tier first.

- **Sell or upgrade:** a verdict for every essence type, plus a stash planner. Enter what you hold and it says what to vendor and what to sell.
- **Flips:** buy a lower tier, vendor it up and sell the higher tier. Shows profit per flip, return %, and how many flips per day the market can absorb, with your own buy markup and sell discount.
- **Special essences:** Insanity, Horror, Delirium, Hysteria and the rest, with volume and 7-day trend.

## How prices update

poe.ninja doesn't allow browsers to fetch its data directly, so a GitHub Actions
workflow (`.github/workflows/pages.yml`) runs `build_data.py` every hour and
redeploys the site with fresh price files. Pages prices can be up to about an hour old.

## Run locally (live prices)

```
python essence_calc.py
```

This needs Python 3.9+ and nothing else. It opens http://127.0.0.1:8765 and fetches
poe.ninja on demand, using a 5-minute cache.
