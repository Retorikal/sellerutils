import csv
import logging
from database.Price import Prices
from collections.abc import Iterable


class Stocks():
  def __init__(self, filepath: str, prices: Prices):
    self.pricemul = 100
    self.filepath = filepath
    self.prices = prices

  def parse(self) -> Iterable[dict]:
    with open(self.filepath) as file:
      reader = csv.reader(file, delimiter=",")
      next(reader)
      for stock_row in reader:
        for card_detail in self.__iterate_stock_entry(stock_row):
          yield card_detail

  def __iterate_stock_entry(self, stock_row: list[str]) -> dict:
    card_id = stock_row[0]
    stock = stock_row[1:]
    name, main_prices, alt_prices, alt_names = self.prices.get_prices(card_id)
    index = 0

    def get_image() -> str:
      return card_id + (f"_P{index}" if index > 0 else "")

    for variant in main_prices:
      if index >= len(stock):
        continue

      if stock[index] != '' and int(stock[index]) > 0:
        desc_list = f"{card_id}\n"
        key_spec = int(variant[-1])
        if card_id == "BT13-101":
          print(card_id, key_spec)
        if key_spec >= 1:
          desc_list += f"Parallel {key_spec} \n"

        yield {
          "CARDCODE": card_id,
          "CARDNAME": name,
          "CARDDESC": desc_list.strip(),
          "PRICE": main_prices[variant] * self.pricemul,
          "STOCK": int(stock[index]),
          "CARDIMG": get_image()
        }

      index += 1

    for variant in alt_prices:
      if index >= len(stock):
        continue

      if stock[index] != '' and int(stock[index]) > 0 and variant[0] != "_":
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

        yield {
          "CARDCODE": card_id,
          "CARDNAME": name,
          "CARDDESC": desc_list.strip(),
          "PRICE": alt_prices[variant] * self.pricemul,
          "STOCK": int(stock[index]),
          "CARDIMG": get_image()
        }

      else:
        if stock[index] != '' and int(stock[index]) > 0 and variant[0] == "_":
          logging.error(f"nonzero stock for skip specifier: {variant}")

      index += 1

    # TODO: Handle index image skipping in digimoncard.dev.
    # Possible method:
    #   add 1 extra field: "custom_image_path"
    #   use skip specifier: "_skip1" : 0

  def __del__(self):
    pass
