import bs4
import json
import logging


class PriceDB():
  def __init__(self, base_db={}) -> None:
    self.db = base_db
    pass

  def __str__(self) -> str:
    return self.db.__str__()

  def register_card(self, card_id):
    if not card_id in self.db:
      self.db[card_id] = {
        "name": "",
        "variants": 0,
        "main_variant": {},
        "alt_variant": {},
      }
      # Probably need to move this declaration somewhere

  def dump(self, filename: str):
    logging.info(f"Dumping to {str}")
    with open("filename", "w") as outfile:
      json.dump(self.db, outfile)

  # code: card code
  # price: price
  # consequent: n-th consequential appearance of this card
  # boosterSource: what page is the card from
  def add_card(self, card_id: str, price: int, consequent=1, booster_source=""):
    if not card_id in self.db:
      self.register_card(card_id)

    if booster_source == "" or booster_source.upper() in card_id.upper():
      print(self.db[card_id])
      cluster = self.db[card_id]["main_variant"]
      size = len(cluster)
      card_id = f"p{size}"
      cluster[card_id] = price
    else:
      cluster = self.db[card_id]["alt_variant"]
      card_id = f"{booster_source}-p{consequent}"
      if card_id in cluster:
        cluster[card_id] = price
      else:
        cluster[f"_{card_id}"] = price

    return
