"""Poll Binance PEPE top-of-book data and store it in Supabase."""

import logging
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from supabase import create_client


BINANCE_BOOK_TICKER_URL = "https://api.binance.com/api/v3/ticker/bookTicker"
POLL_INTERVAL_SECONDS = 1.0


def load_configuration():
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    symbol = os.getenv("BINANCE_SYMBOL", "PEPEUSDT").upper()

    if not supabase_url or not service_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the environment."
        )

    return supabase_url, service_key, symbol


def fetch_book_ticker(session, symbol):
    response = session.get(
        BINANCE_BOOK_TICKER_URL,
        params={"symbol": symbol},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    return {
        "symbol": symbol,
        "best_bid_price": float(payload["bidPrice"]),
        "best_bid_quantity": float(payload["bidQty"]),
        "best_ask_price": float(payload["askPrice"]),
        "best_ask_quantity": float(payload["askQty"]),
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    supabase_url, service_key, symbol = load_configuration()
    supabase = create_client(supabase_url, service_key)

    logging.info("Starting Binance %s top-of-book collector", symbol)
    with requests.Session() as session:
        while True:
            started_at = time.monotonic()
            try:
                record = fetch_book_ticker(session, symbol)
                supabase.table("pepe_data").insert(record).execute()
                logging.info(
                    "%s bid=%s (%s) ask=%s (%s)",
                    record["symbol"],
                    record["best_bid_price"],
                    record["best_bid_quantity"],
                    record["best_ask_price"],
                    record["best_ask_quantity"],
                )
            except (KeyError, requests.RequestException, ValueError, RuntimeError) as error:
                logging.exception("Could not collect or upload market data: %s", error)
            except Exception:
                logging.exception("Unexpected Supabase or collector error")

            elapsed = time.monotonic() - started_at
            time.sleep(max(0.0, POLL_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    main()