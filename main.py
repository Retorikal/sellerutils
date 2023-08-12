import csv
from pricescraper.PriceDB import PriceDB as PDB

import logging


def parse_stocks(filepath):
  with open(filepath) as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)
    for row in reader:
      yield (row[0], [int(i) for i in row[1:] if i != ''])


def tokopedia_push_stock(card_id, variant):
  pass


def add_stocks(stock_file, prices_file, dry_run=True):
  db = PDB(prices_file)
  warn_counters = 0

  for card_id, stocks in parse_stocks(stock_file):
    name, prices_main, prices_alt = db.prices(card_id)

    for variant, stock in zip(prices_main.keys(), stocks):
      logging.info(f"{card_id} {name}: {variant} ({stock} pcs) added")
      if not dry_run:
        tokopedia_push_stock()

    for variant, stock in zip(prices_alt.keys(), stocks):
      if variant[0] == "_":
        logging.warning(
          f"add_stocks, {card_id} {name}: {variant} is not identified. Skipping")
        warn_counters += 1
        continue

      logging.info(f"{card_id} {name}: {variant} ({stock} pcs) added")
      if not dry_run:
        tokopedia_push_stock()

  if warn_counters == 0:
    logging.info(f"{warn_counters} warnings")

  else:
    logging.warning(f"{warn_counters} warnings, double check {prices_file}")

  return warn_counters


logging.basicConfig(level=logging.INFO)
add_stocks("./db/samplestock.csv", "./db/nameprices.json")
