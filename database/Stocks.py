import csv
import logging
from typing import Any, Generator
from database.Price import Prices
from collections.abc import Iterable


class Stocks():
  """
  Creates an iterable based on two database files:
  `stockpath`: CSV file containing how much stock is available for a given card ID
  `pricespath`: Dictionary file containing how much should a given card ID sell for
  """

  def __init__(self, stockpath: str, pricespath: str):
    self.rate = 100
    self.stockpath = stockpath
    self.prices = Prices(pricespath)

  def parse_stock(self) -> Iterable[dict[str, Any]]:
    """ 
    Iterates `self.stockpath` and returns a `dict` with the following entries for each card:
    ```
    dict{
      "CARDCODE": # Card's full code qualifier plus parallel notation, ex: BT11-023_P1,
      "CARDNAME": # Card's full name,
      "TITLEDESC": # Inline short description,
      "CARDDESC": # Full string for product description in shop listing,
      "PRICE": # Price in idr: yyt * 100,
      "STOCK": # Amount of card in stock,
      "CARDSKU": # Card image filename
    }
    ```
    """
    with open(self.stockpath) as file:
      reader = csv.reader(file, delimiter=",")
      next(reader)
      for stock_row in reader:
        for card_detail in self.__iterate_stock_entry(stock_row):
          yield card_detail

  def __iterate_stock_entry(self, stock_row: list[str]) -> Generator[dict[str, Any], Any, Any]:
    card_id = stock_row[0]
    stocks = stock_row[1:]
    name, main_prices, alt_prices, alt_names = self.prices.get_prices(card_id)

    def get_image() -> str:
      return card_id + (f"_P{index}" if index > 0 else "")

    for index, variant in enumerate(main_prices):
      if index >= len(stocks):
        continue

      try:
        count = int(stocks[index])
      except:
        count = 0

      if count == 0:
        continue

      desc_list = f"{card_id}\n"
      key_spec = int(variant[-1])
      if card_id == "BT13-101":
        print(card_id, key_spec)
      if key_spec >= 1:
        desc_list += f"Parallel {key_spec} \n"
      desc_list = desc_list.strip()

      yield {
        "CARDCODE": card_id,
        "CARDNAME": name,
        "CARDDESC": desc_list,
        "TITLEDESC": desc_list.replace("\n", ", "),
        "PRICE": main_prices[variant] * self.rate,
        "STOCK": int(stocks[index]),
        "CARDSKU": get_image()
      }

      index += 1

    for variant in alt_prices:
      if index >= len(stocks):
        continue

      if stocks[index] != '' and int(stocks[index]) > 0 and variant[0] != "_":
        desc_list = f"{card_id}\n"
        booster_source, _ = variant.split("-")

        if booster_source == "P":
          if variant in alt_names:
            desc_list += f"{alt_names[variant]}\n"
          else:
            logging.error(
              f"{card_id}: {variant} specific origin unspecified. Please add first.")
        # else if booster_source == "LM":
        #  pass
        else:
          key_spec = int(variant[-1])
          desc_list += f"{booster_source} Reprint\n"
          if key_spec >= 1:
            desc_list += f"Parallel{ f' {key_spec}' if key_spec > 1 else ''}"

        desc_list = desc_list.strip()

        yield {
          "CARDCODE": card_id,
          "CARDNAME": name,
          "CARDDESC": desc_list,
          "TITLEDESC": desc_list.replace("\n", ", "),
          "PRICE": alt_prices[variant] * self.rate,
          "STOCK": int(stocks[index]),
          "CARDSKU": get_image()
        }

      else:
        if stocks[index] != '' and int(stocks[index]) > 0 and variant[0] == "_":
          logging.error(f"nonzero stock for skip specifier: {variant}")

      index += 1

    # TODO: Handle index image skipping in digimoncard.dev.
    # Possible method:
    #   add 1 extra field: "custom_image_path"
    #   use skip specifier: "_skip1" : 0

  def __del__(self):
    pass
