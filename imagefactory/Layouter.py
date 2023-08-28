#!/usr/bin/python3
from os.path import exists
from typing import Generator
from xml.etree import ElementTree
from datetime import datetime
from string import Template
from pricefetcher.PriceDB import PriceDB as PDB
import logging
import cairosvg
import copy
import math
import wget
import cairosvg
import re

now = datetime.now
default_template = "template/template_a3_port.svg"
default_outdir = "imgcache/"
default_cardimg_idr = "imgcache/cardimg/"
jp_url = "https://en.digimoncard.com/images/cardlist/card/{}.png"


class Layouter():
  def __init__(self, template_path: str) -> None:
    self.template_path = template_path
    self.out_dir = default_outdir
    self.cardimg_dir = default_cardimg_idr
    self.repl_dict = {}

    def repl(m):
      n = m.group(1)
      self.repl_dict[n] = None
      return f"${n}"

    with open(template_path,) as template_file:
      bracket_regex = re.compile("\{(.*)\}")
      file_content = template_file.read()
      template_str = bracket_regex.sub(repl, file_content)
      self.template = Template(template_str)

    logging.info(f"Layouter, created with template {template_path}")

  def craft_images_from_stock(self, db: PDB, stock_entries: list[str]):
    for name_paragraph, price, img_url in self.__iterate_stock(db, stock_entries):
      print(name_paragraph, price, img_url)
      pass
    pass

  def __iterate_stock(self, db: PDB, stock_entries: list[list[str]]) -> Generator[list[str], int, str]:
    for stock_entry in stock_entries:
      card_id = stock_entry[0]
      stock = stock_entry[1:]
      name, main_prices, alt_prices, alt_names = db.get_prices(card_id)
      index = 0

      def get_image() -> str:
        return card_id + (f"_P{index}" if index > 0 else "") + ".png"

      for variant in main_prices:
        if index >= len(stock):
          continue

        if int(stock[index]):
          name_list = [card_id, name]
          key_spec = int(variant[-1])
          if key_spec > 1:
            name_list.append("Parallel" + f" {key_spec}")

          yield (name_list, main_prices[variant], get_image())

        index += 1

      for variant in alt_prices:
        if index >= len(stock):
          continue

        if int(stock[index]) > 0 and variant[0] != "_":
          name_list = [card_id, name]
          booster_source, _ = variant.split("-")

          if booster_source == "P":
            if variant in alt_names:
              name_list.append(alt_names[variant])
            else:
              logging.error(
                f"{variant} specific origin unspecified. Please add first.")
          else:
            key_spec = int(variant[-1])
            name_list.append(f"{booster_source} reprint")
            if key_spec > 1:
              name_list.append(
                  "Parallel" + f" {key_spec}" if key_spec > 1 else "")

          yield (name_list, alt_prices[variant], get_image())
        else:
          if stock[index] > 0 and variant[0] == "_":
            logging.error(f"nonzero stock for skip specifier: {variant}")

        index += 1

    # TODO: Handle index image skipping in digimoncard.dev.
    # Possible method:
    #   add 1 extra field: "custom_image_path"
    #   use skip specifier: "_skip1" : 0

  def get_card_images(self, cardlist):
    logging.info("Parsing cardlist and downloading images..")
    for entry in cardlist:
      filename = f"{self.cardimg_dir}{entry}.png"
      if not exists(filename):
        logging.info(f"Downloading {entry}.png image")
        wget.download(jp_url.format(entry), filename)
      else:
        logging.info(f"{filename} exists")
    print(f"Download complete")

    return cardlist


# logging.basicConfig(level=logging.INFO)
# a = Layouter("./imagefactory/templates/templateDigi.svg")
# a.get_card_images(["BT9-109", "BT9-109_P1"])
