import csv
import json
import logging
from pricescraper.PriceDB import PriceDB as DB
from pricescraper.YuyuteiScraper import YuyuteiScraper as YYSc
from pricescraper import digimoncard


def parse_stocks(filepath):
  stock_dict = {}
  with open(filepath) as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)
    for row in reader:
      stock_dict[row[0]] = [int(i) for i in row[1:] if i != '']

  return stock_dict


logging.basicConfig(level=logging.INFO)


# sc = YYSc()
# sc.price_dict = {}
# sc.scrape_prices_regular(
#   "https://yuyu-tei.jp//game_digi/sell/sell_price.php?ver=ex03")

# db = DB("db/nameprices.json")
db = DB("db/nameprices.json")
# db.refresh_prices(YYSc())
# db.dump()

stocks = parse_stocks("db/samplestock.csv")

print(stocks)
card_id = "BT14-044"
name, variants = db.prices(card_id)
print(f"{card_id} {name} {variants}")
