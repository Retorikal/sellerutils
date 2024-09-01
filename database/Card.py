from dataclasses import dataclass
import os.path
import json
import logging
from fetcher.cardnames import digimoncard
from fetcher.price.IScraper import IScraper


@dataclass
class CardEntry():
  name: str
  id: str
  variant_prices: dict
  variant_names: dict


class CardDB():
  def __init__(self, filesrc="", base_db={}, base_rate=100) -> None:
    self.filesrc = filesrc
    if filesrc != "" and os.path.exists(filesrc):
      with open(filesrc) as file:
        value = json.load(file)
        self.db = value["db"]
        self.rate = value["rate"]
    else:
      logging.warn("PriceDB, __init__, file not specified or does not exist")
      self.db = base_db
      self.rate = base_rate
    pass

  def __str__(self) -> str:
    return self.db.__str__()

  def refresh(self, scraper: IScraper, dump=True):
    scraper.scrape_update(self.db)

    if dump:
      self.dump_file()

  def get_price_sku(self, card_sku: str):
    card_identifiers = card_sku.split("_")
    card_id = card_identifiers[0]
    card_alt_idx = int(card_identifiers[1][1:]) if len(
      card_identifiers) > 1 else 0

    main_size = len(self.db[card_id]["main"])
    if card_alt_idx < main_size:
      keys = list(self.db[card_id]["main"].keys())
      key = keys[card_alt_idx]
      return self.db[card_id]["main"][key]

    keys = list(self.db[card_id]["alt"].keys())
    key = keys[card_alt_idx - main_size]
    return self.db[card_id]["alt"][key]

  def get_entry_by_id(self, card_id) -> CardEntry:
    price = CardEntry(
      id=card_id,
      name=self.db[card_id]["name"],
      variant_prices=self.db[card_id]["variants"],
      variant_names=self.db[card_id]["varnames"]
    )

    return price

  def dump_file(self, filename=""):
    targetfile = filename if filename != "" else self.filesrc
    logging.info(f"dump start, dumping to {targetfile}")

    with open(targetfile, "w") as outfile:
      value = {
        'rate': self.rate,
        'db': self.db
          }
      json.dump(value, outfile)

  # code: card code
  # price: price
  # consequent: n-th consequential appearance of this card
  # boosterSource: what page is the card from
