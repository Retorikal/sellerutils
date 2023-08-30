#!/usr/bin/python3
from os.path import exists
from datetime import datetime
from string import Template
from pricefetcher.PriceDB import PriceDB as PDB
import logging
import wget
import re
import os
from collections.abc import Iterable

now = datetime.now
default_sandbox_dir = "workspace/sandbox"
default_img_dir = "workspace/sandbox/images/"
default_out_dir = "workspace/output/"
jp_url = "https://en.digimoncard.com/images/cardlist/card/{}.png"


class Layouter():
  def __init__(self, template_path: str) -> None:
    self.template_path = template_path
    self.sandbox_dir = os.path.join(os.getcwd(), default_sandbox_dir)
    self.img_dir = os.path.join(os.getcwd(), default_img_dir)
    self.out_dir = os.path.join(os.getcwd(), default_out_dir)
    self.repl_dict = {}

    def subs_template_format(m):
      n = m.group(1)
      self.repl_dict[n] = None
      return f"${n}"

    with open(template_path,) as template_file:
      bracket_regex = re.compile("\{(.*)\}")
      file_content = template_file.read()
      template_str = bracket_regex.sub(
        subs_template_format, file_content)
      self.template = Template(template_str)

    logging.info(f"Layouter, created with template {template_path}")

  def craft_images_from_stock(self, db: PDB, stock_entries: Iterable[tuple[str, list[str]]], force_update=False):
    for name, desc, price, card_image_id in self.__iterate_stock(db, stock_entries):
      image = self.get_card_image(card_image_id)

      self.repl_dict["CARDNAME"] = name
      self.repl_dict["CARDDESC"] = desc
      self.repl_dict["CARDIMG"] = os.path.join(self.img_dir, card_image_id)

      svg_string = self.template.substitute(self.repl_dict)
      filename = os.path.join(self.sandbox_dir, f"{card_image_id}.svg")
      if not exists(filename) or force_update:
        logging.info(f"writing image {filename}")
        with open(filename, "w") as svg_file:
          svg_file.write(svg_string)
      else:
        logging.info(f"{filename} exists!")

    os.system(
      f'inkscape --actions="export-type:png;export-do;" {self.sandbox_dir}/*.svg')
    os.system(f'mv {self.sandbox_dir}/*.png {self.out_dir}/')
    os.system(f'mv {self.sandbox_dir}/*.svg {self.out_dir}/')
    # save svg string

  def __iterate_stock(self, db: PDB, stock_entries: (str, list[str])) -> Iterable[str, str, int, str]:
    for card_id, stock in stock_entries:
      name, main_prices, alt_prices, alt_names = db.get_prices(card_id)
      index = 0

      def get_image() -> str:
        return card_id + (f"_P{index}" if index > 0 else "")

      for variant in main_prices:
        if index >= len(stock):
          continue

        if int(stock[index]):
          desc_list = f"{card_id}\n"
          key_spec = int(variant[-1])
          if key_spec > 1:
            desc_list += f"Parallel {key_spec} \n"

          yield (name, desc_list, main_prices[variant], get_image())

        index += 1

      for variant in alt_prices:
        if index >= len(stock):
          continue

        if int(stock[index]) > 0 and variant[0] != "_":
          desc_list = f"{card_id}\n"
          booster_source, _ = variant.split("-")

          if booster_source == "P":
            if variant in alt_names:
              desc_list += f"{alt_names[variant]}\n"
            else:
              logging.error(
                f"{variant} specific origin unspecified. Please add first.")
          else:
            key_spec = int(variant[-1])
            desc_list += f"{booster_source} reprint\n"
            if key_spec > 1:
              desc_list += f"Parallel{ f' {key_spec}' if key_spec > 1 else ''}"

          yield (name, desc_list, alt_prices[variant], get_image())
        else:
          if stock[index] > 0 and variant[0] == "_":
            logging.error(f"nonzero stock for skip specifier: {variant}")

        index += 1

    # TODO: Handle index image skipping in digimoncard.dev.
    # Possible method:
    #   add 1 extra field: "custom_image_path"
    #   use skip specifier: "_skip1" : 0

  def get_card_image(self, entry):
    filename = os.path.join(self.img_dir, f"{entry}.png")
    if not exists(filename):
      logging.info(f"Downloading {entry}.png image")
      out = wget.download(jp_url.format(entry), filename)
      return out
    else:
      logging.info(f"{filename} exists")
    print(f"Download complete")


# logging.basicConfig(level=logging.INFO)
# a = Layouter("./imagefactory/templates/templateDigi.svg")
# a.get_card_images(["BT9-109", "BT9-109_P1"])
