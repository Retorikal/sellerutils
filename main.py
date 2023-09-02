
from database.Price import Prices
from database.Stocks import Stocks
from factory.image.SVGTemplate import SVGTemplate
from factory.uploadfile.Tokopedia import Tokopedia

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
  db = Prices(prices_file)
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


stockpath = "workspace/static/samplestock.csv"
stockid = stockpath.split("/")[-1].split(".")[0]

pricespath = "workspace/db/nameprices.json"
templatepath = "workspace/static/templates/templateDigi.svg"
tokopediapath = f"workspace/output/{stockid}.xlsx"

db = Prices(pricespath)
imgfactory = SVGTemplate(templatepath)
tokopedia = Tokopedia(tokopediapath)
stocks = Stocks(stockpath, db)

for stock in stocks.parse():
  imgfactory.generate_from_stock_entry(db, stock)
  tokopedia.populate_from_stock_entry(db, stock)

imgfactory.dump_results()
tokopedia.save()
