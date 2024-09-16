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
  variants: list
  variant_prices: dict
  variant_images: dict
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
    variant = card_identifiers[1] if len(card_identifiers) > 0 else "p0"

    return self.db[card_id]["prices"][variant]

  def get_entry_by_id(self, card_id) -> CardEntry:
    price = CardEntry(
      id=card_id,
      name=self.db[card_id]["name"],
      variants=self.db[card_id]["variants"],
      variant_prices=self.db[card_id]["prices"],
      variant_images=self.db[card_id]["images"],
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
