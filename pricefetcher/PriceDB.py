import os.path
import json
import logging
from namefetcher import digimoncard
from pricefetcher.scrapers import Scraper


class PriceDB():
  def __init__(self, filesrc="", base_db={}) -> None:

    self.filesrc = filesrc
    if filesrc != "" and os.path.exists(filesrc):
      with open(filesrc) as file:
        self.db = json.load(file)
    else:
      logging.warn("PriceDB, __init__, file not specified or does not exist")
      self.db = base_db
    pass

  def __str__(self) -> str:
    return self.db.__str__()

  def refresh_prices(self, scraper: Scraper, dump=True):
    scraper.scrape_update(self.db)

    if dump:
      self.dump_file()

  def get_prices(self, card_id) -> tuple[str, dict, dict, dict]:
    return (
        self.db[card_id]["name"],
        self.db[card_id]["main_variant"],
        self.db[card_id]["alt_variant"],
        self.db[card_id]["variant_names"],
      )

  def dump_file(self, filename=""):
    targetfile = filename if filename != "" else self.filesrc
    logging.info(f"dump start, dumping to {targetfile}")

    with open(targetfile, "w") as outfile:
      json.dump(self.db, outfile)

  # code: card code
  # price: price
  # consequent: n-th consequential appearance of this card
  # boosterSource: what page is the card from
