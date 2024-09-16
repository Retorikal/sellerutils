import os

user_config = f"{os.path.expanduser('~')}/.rtcgtools"
root_config = f"{os.path.dirname(os.path.abspath(__file__))}/configs"


def db_path():
  return f"{user_config}/card_db.json"


def template_svg_path():
  return f"{root_config}/templateDigi.svg"


def card_images_path():
  return f"{user_config}/cardimages/"


def template_xls_path():
  return f"{root_config}/tambah-sekaligus.xlsx"


def product_default_path():
  return f"{root_config}/productdescdefaults.json"
