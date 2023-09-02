#!/usr/bin/python3
from os.path import exists
from datetime import datetime
from string import Template
from database.Price import Prices as Prices
import logging
import wget
import re
import os

now = datetime.now
default_sandbox_dir = "workspace/sandbox"
default_img_dir = "workspace/sandbox/images/"
default_out_dir = "workspace/output/images"
jp_url = "https://en.digimoncard.com/images/cardlist/card/{}.png"


class SVGTemplate():
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

  def dump_results(self):
    os.system(
      f'inkscape --actions="export-type:png;export-do;" {self.sandbox_dir}/*.svg')
    os.system(f'mv {self.sandbox_dir}/*.png {self.out_dir}/')
    # os.system(f'mv {self.sandbox_dir}/*.svg {self.out_dir}/')

  def generate_from_stock_entry(self, db: Prices, card_details: dict, force_update=True):
    card_details['SVGTEMPLATE_CARDIMG'] = f"{self.img_dir}{card_details['CARDIMG']}.png"
    svg_string = self.template.substitute(card_details)
    filename = os.path.join(
      self.sandbox_dir, f"{card_details['CARDIMG']}.svg")
    if not exists(filename) or force_update:
      logging.info(f"writing image {filename}")
      with open(filename, "w") as svg_file:
        svg_file.write(svg_string)
    else:
      logging.info(f"{filename} exists!")
    # save svg string

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
# a = Layouter("./factory.image/templates/templateDigi.svg")
# a.get_card_images(["BT9-109", "BT9-109_P1"])
