
from pricefetcher.PriceDB import PriceDB as PDB
from pricefetcher.scrapers.YYTScraper import YYTDigiScraper as YYTScraper
from imagefactory.Layouter import Layouter
from uploadfilefactory.tokopedia import Tokopedia

import logging
import csv

logging.basicConfig(level=logging.INFO)


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
    name, prices_main, prices_alt = db.get_prices(card_id)

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


stockfile = "workspace/static/samplestock.csv"
stockid = stockfile.split("/")[-1]

db = PDB("workspace/db/nameprices.json")
mock_stock = [
  ("BT10-030", ["1"]),
  ("BT9-109", ["1", "1"]),
]
layouter = Layouter("workspace/templates/templateDigi.svg")
layouter.craft_images_from_stock(
  db, parse_stocks("workspace/static/samplestock.csv"))

tokopedia = Tokopedia(f"workspace/output/{stockid}.xlsx")
tokopedia.add_entry_from_stock(
  db, parse_stocks("workspace/static/samplestock.csv"))

# db = PDB("workspace/db/nameprices.json")
# db.refresh_prices(YYTScraper(), True)

# add_stocks("./db/samplestock.csv", "./db/nameprices.json")
