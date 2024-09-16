#!/usr/bin/python3
from os.path import exists
from datetime import datetime
from string import Template
from typing import Any
from database.Card import CardDB as CardDB
import configs
import logging
import html
import wget
import re
import os
from pathlib import Path
import shutil
import tempfile

from database.Stocks import StockEntry, StockDB

jp_url = "https://en.digimoncard.com/images/cardlist/card/{}"


class SVGGenerator():
  def __init__(self, out_path, template_path: str = "") -> None:
    if not template_path:
      template_path = configs.template_svg_path()

    self.template_path = template_path
    self.sandbox_dir = os.path.join(tempfile.gettempdir(), "rtcgsandbox")
    self.img_dir = os.path.join(os.getcwd(), configs.card_images_path())
    self.out_dir = os.path.join(os.getcwd(), out_path)
    self.repl_dict = {}

    shutil.rmtree(self.sandbox_dir)
    Path(self.sandbox_dir).mkdir(parents=True, exist_ok=True)
    Path(self.img_dir).mkdir(parents=True, exist_ok=True)

    def subs_template_format(m):
      n = m.group(1)
      self.repl_dict[n] = None
      return f"${n}"

    with open(template_path) as template_file:
      bracket_regex = re.compile(r"\{(.*)\}")
      file_content = template_file.read()
      template_str = bracket_regex.sub(
        subs_template_format, file_content)
      self.template = Template(template_str)

    logging.info(f"Layouter, created with template {template_path}")

  def generate_images(self, stocks: StockDB, force_update=True):

    for stock in stocks.parse_stock():
      self.__generate_image(stock, force_update)
    pass

    os.system(
      f'inkscape --actions="export-type:png;export-do;" {self.sandbox_dir}/*.svg')
    os.system(f'mv {self.sandbox_dir}/*.png {self.out_dir}/')

  def __generate_image(self, stock: StockEntry, force_update=True):
    """
    Accepts `stock` and generates an appropriate svg file
    @param `force_update`: bool, if true will overwrite previous image
    """
    card_details: dict[str, Any] = stock.get_dict()
    card_details['SVG_IMAGE_PATH'] = f"{self.img_dir}{stock.image_id}"
    card_details['SVG_CARDNAME'] = html.escape(card_details['CARDNAME'])

    svg_string = self.template.substitute(card_details)
    filename = os.path.join(
      self.sandbox_dir, f"{stock.stock_id}.svg")
    self.__get_card_image(stock.image_id)
    if not exists(filename) or force_update:
      logging.info(f"writing image {filename}")
      with open(filename, "w") as svg_file:
        svg_file.write(svg_string)
    else:
      logging.info(f"{filename} exists!")

  def __get_card_image(self, entry):
    filename = os.path.join(self.img_dir, entry)
    if not exists(filename):
      logging.info(f"Downloading {entry} image")
      out = wget.download(jp_url.format(entry), filename)
      return out
    else:
      logging.info(f"{filename} exists")
    print(f"Download complete")


# logging.basicConfig(level=logging.INFO)
# a = Layouter("./factory.image/templates/templateDigi.svg")
# a.get_card_images(["BT9-109", "BT9-109_P1"])
