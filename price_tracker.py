#!/usr/bin/env python3
"""
Price Tracker
=============
Monitor product prices on any website. Stores history in JSON,
detects price drops, and can export to CSV.

Features:
    - Add/remove products to track
    - Automatic price extraction from HTML
    - Price change detection with alerts
    - Target-price notifications
    - CSV history export

Usage:
    python price_tracker.py          # Interactive mode
    python price_tracker.py --help   # Show help

Learn more: https://raccoonette.gumroad.com/l/Python-for-automating-every-day-tasks
"""

import re
import sys
import json
import time
from pathlib import Path
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class PriceTracker:
    """Track product prices over time with change detection and alerts."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    PRICE_SELECTORS = [
        ".price", ".product-price", ".current-price",
        "#price", "#product-price", "#priceblock_ourprice",
        "[data-price]", '[itemprop="price"]',
        ".sale-price", ".final-price",
    ]

    CURRENCY_SYMBOLS = {"$": "USD", "EUR": "EUR", "GBP": "GBP", "JPY": "JPY"}

    def __init__(self, data_file: str = "price_data.json"):
        self.data_file = Path(data_file)
        self.data = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if self.data_file.exists():
            with open(self.data_file, "r") as fh:
                return json.load(fh)
        return {"products": {}}

    def _save(self):
        with open(self.data_file, "w") as fh:
            json.dump(self.data, fh, indent=2, default=str)

    # ------------------------------------------------------------------
    # Price parsing helpers
    # ------------------------------------------------------------------

    @classmethod
    def _parse_price(cls, text: str):
        """Return (price_float, currency_str) from a string like '$99.99'."""
        currency = "USD"
        for sym, code in cls.CURRENCY_SYMBOLS.items():
            if sym in text:
                currency = code
                break
        matches = re.findall(r"[\d,]+\.?\d*", text)
        for m in matches:
            try:
                val = float(m.replace(",", ""))
                if val > 0:
                    return val, currency
            except ValueError:
                continue
        return None, None

    def _extract_price(self, url: str):
        """Fetch *url* and try multiple strategies to find the price."""
        try:
            resp = requests.get(url, headers=self.DEFAULT_HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"  Fetch error: {exc}")
            return None, None

        soup = BeautifulSoup(resp.content, "lxml")

        # Strategy 1: common CSS selectors
        for sel in self.PRICE_SELECTORS:
            for el in soup.select(sel):
                if el.has_attr("data-price"):
                    try:
                        return float(el["data-price"]), "USD"
                    except ValueError:
                        pass
                if el.has_attr("content"):
                    try:
                        return float(el["content"]), "USD"
                    except ValueError:
                        pass
                price, cur = self._parse_price(el.get_text())
                if price:
                    return price, cur

        # Strategy 2: regex scan of full page text
        patterns = [
            r"\$\s*[\d,]+\.?\d*",
            r"[\d,]+\.?\d*\s*(?:USD|EUR|GBP)",
            r"\u20ac\s*[\d,]+\.?\d*",
            r"\u00a3\s*[\d,]+\.?\d*",
        ]
        page_text = soup.get_text()
        for pat in patterns:
            found = re.findall(pat, page_text)
            if found:
                price, cur = self._parse_price(found[0])
                if price:
                    return price, cur

        print("  Could not detect price on page")
        return None, None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_product(self, name: str, url: str, target_price: float = None):
        pid = name.lower().replace(" ", "_")
        self.data["products"][pid] = {
            "name": name,
            "url": url,
            "target_price": target_price,
            "price_history": [],
            "created": datetime.now().isoformat(),
        }
        self._save()
        print(f"Added: {name}")
        self.check_price(pid)

    def remove_product(self, product_id: str):
        if product_id in self.data["products"]:
            name = self.data["products"][product_id]["name"]
            del self.data["products"][product_id]
            self._save()
            print(f"Removed: {name}")
        else:
            print(f"Not found: {product_id}")

    def check_price(self, product_id: str):
        prod = self.data["products"].get(product_id)
        if not prod:
            print(f"Not found: {product_id}")
            return

        print(f"Checking: {prod['name']}")
        price, currency = self._extract_price(prod["url"])
        if price is None:
            return

        record = {"price": price, "currency": currency, "timestamp": datetime.now().isoformat()}

        prev = prod["price_history"][-1]["price"] if prod["price_history"] else None
        if prev is not None:
            change = price - prev
            pct = (change / prev) * 100
            record["change"] = change
            record["change_percent"] = pct

        prod["price_history"].append(record)
        self._save()

        print(f"  Price: {currency} {price:.2f}")
        if prev is not None:
            diff = price - prev
            if diff > 0:
                print(f"  +{currency} {diff:.2f} ({pct:+.1f}%)")
            elif diff < 0:
                print(f"  {currency} {diff:.2f} ({pct:+.1f}%)")
            else:
                print("  Price unchanged")

        if prod["target_price"] and price <= prod["target_price"]:
            print(f"  *** ALERT: at or below target {currency} {prod['target_price']:.2f} ***")

    def check_all(self):
        print("Checking all products...")
        print("=" * 50)
        for pid in self.data["products"]:
            self.check_price(pid)
            print()
            time.sleep(2)

    def list_products(self):
        print("Tracked products:")
        print("-" * 50)
        for pid, prod in self.data["products"].items():
            latest = prod["price_history"][-1] if prod["price_history"] else None
            price_str = f"{latest['currency']} {latest['price']:.2f}" if latest else "N/A"
            target_str = f" (target: {prod['target_price']})" if prod["target_price"] else ""
            print(f"  [{pid}] {prod['name']} - {price_str}{target_str}")

    def export_csv(self, product_id: str, filename: str = None):
        prod = self.data["products"].get(product_id)
        if not prod:
            print(f"Not found: {product_id}")
            return

        filename = filename or f"{product_id}_history.csv"
        with open(filename, "w") as fh:
            fh.write("timestamp,price,currency,change,change_percent\n")
            for r in prod["price_history"]:
                fh.write(
                    f"{r['timestamp']},{r['price']},{r['currency']},"
                    f"{r.get('change', '')},{r.get('change_percent', '')}\n"
                )
        print(f"Exported to: {filename}")


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    tracker = PriceTracker("price_data.json")
    print("Price Tracker")
    print("=" * 50)
    print("Commands: add, remove, check, check-all, list, history, export, quit")
    print()

    while True:
        try:
            parts = input(">>> ").strip().split()
            if not parts:
                continue
            cmd = parts[0].lower()

            if cmd in ("quit", "exit"):
                break
            elif cmd == "add" and len(parts) >= 3:
                target = float(parts[3]) if len(parts) > 3 else None
                tracker.add_product(parts[1], parts[2], target)
            elif cmd == "remove" and len(parts) >= 2:
                tracker.remove_product(parts[1])
            elif cmd == "check" and len(parts) >= 2:
                tracker.check_price(parts[1])
            elif cmd == "check-all":
                tracker.check_all()
            elif cmd == "list":
                tracker.list_products()
            elif cmd == "history" and len(parts) >= 2:
                hist = tracker.data["products"].get(parts[1], {}).get("price_history", [])
                for r in hist[-10:]:
                    print(f"  {r['timestamp']}: {r['currency']} {r['price']:.2f}")
            elif cmd == "export" and len(parts) >= 2:
                tracker.export_csv(parts[1])
            else:
                print("Unknown command. Try: add, remove, check, check-all, list, history, export, quit")
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
