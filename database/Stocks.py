import csv
import logging
from typing import Any, Generator
from database.Card import CardDB
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class StockEntry():
  code: str
  name: str
  subtitle: str
  desc: str
  price: int
  stock: int
  stock_id: str
  image_id: str

  def get_dict(self) -> dict[str, Any]:
    return {
      "CARDCODE": self.code,  # Card code qualifier + par notation, ex: BT11-023_P1,
      "CARDNAME": self.name,  # Card's full name,
      "TITLEDESC": self.subtitle,  # Inline short description,
      "CARDDESC": self.desc,  # Full string for product description in shop listing,
      "PRICE": self.price,  # Price in idr: yyt * 100,
      "STOCK": self.stock,  # Amount of card in stock,
      "CARDSKU": self.stock_id,  # Card stock ID
    }


class StockDB():
  """
  Creates an object representing all the owned stocks.:
  `stockpath`: CSV file containing how much stock is available for a given card ID
  `pricespath`: Dictionary file containing how much should a given card ID sell for
  """

  def __init__(self, stockpath: str, db: CardDB):
    self.prices = db
    self.rate = db.rate
    self.stockpath = stockpath

  def parse_stock(self) -> Iterable[StockEntry]:
    """ 
    Iterates `self.stockpath` and returns `Stock` object for each:
    """
    with open(self.stockpath) as file:
      reader = csv.reader(file, delimiter=",")
      next(reader)
      for stock_row in reader:
        for card_detail in self.__iterate_stock_entry(stock_row):
          yield card_detail

  def __iterate_stock_entry(self, stock_row: list[str]) -> Generator[StockEntry, Any, Any]:
    card_id = stock_row[0]
    stocks = stock_row[1:]
    card_entry = self.prices.get_entry_by_id(card_id)

    for index, (variant_id, variant_price) in enumerate(card_entry.variant_prices.items()):
      if stocks[index] == '' or int(stocks[index]) == 0:
        continue

      if int(stocks[index]) > 0 and variant_id[0] == "_":
        logging.error(f"nonzero stock for skip specifier: {variant_id}")

      desc_list = [f"{card_id}"]
      variant_name = card_entry.variant_names[variant_id]
      if not variant_name == "":
        desc_list.append(variant_name)

      image_id = card_id
      if index > 0:
        image_id += f"_P{index}"

      variant_string = "" if variant_id[-2:] == "p0" else (
        f"_{variant_id}").upper()

      detail = StockEntry(
        code=card_id,
        name=card_entry.name,
        desc="\n".join(desc_list),
        subtitle=", ".join(desc_list),
        price=variant_price * self.prices.rate,
        stock=int(stocks[index]),
        stock_id=card_id + variant_string,
        image_id=image_id
      )

      yield detail

  def __del__(self):
    pass
