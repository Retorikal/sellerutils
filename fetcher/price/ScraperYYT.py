import requests
import bs4
import re
import logging

from fetcher.cardnames import digimoncard
from fetcher.price.IScraper import IScraper


class ScraperYYTDigi(IScraper):
  def __init__(self) -> None:
    self.url = "https://yuyu-tei.jp/top/digi"
    self.price_dict = {}
    self.ref_dict = {}
    super().__init__()

  def scrape_update(self, price_dict: dict):
    self.ref_dict = digimoncard.get_cardname_dict()
    self.price_dict = price_dict

    cats = self.get_categories()
    promo_cats = [cat for cat in cats if "pr" in cat]
    regular_cats = [cat for cat in cats if not "pr" in cat]

    for cat in regular_cats:
      self.scrape_prices_regular(cat)

    for cat in promo_cats:
      self.scrape_prices_promo(cat)

    self.ref_dict.clear()

  def get_categories(self):
    logging.info("get_categories start")
    page = requests.get(self.url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    singles = soup.find("div", {"id": "side-sell-single"})
    categories = singles.find_all("button", {"onclick": True})
    links = set()
    for category in categories:
      onclick: str = category["onclick"]
      url = onclick.replace("#", "'").split("'")[1]
      links.add(url)

    print(f"{len(links)} links found")

    return links

  def scrape_prices_promo(self, url: str):
    logging.info(f"scrape_prices_promo start, scraping from {url}")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    products = soup.find_all("div", {"class": "card-product"})
    para_count = {}

    for product in products:
      id = product.find("span").text

      pricestrong = product.find("strong").text
      pricefilter = filter(str.isdigit, pricestrong)
      pricestr = "".join(pricefilter)
      price = int(pricestr)

      para_count[id] = para_count[id] + 1 if id in para_count else 0

      self.add_card(id, price, para_count[id], "P")

  def scrape_prices_regular(self, url: str):
    logging.info(f"scrape_prices_regular start, scraping from {url}")
    booster_url_specifier = url.split("/")[-1].upper()
    booster_parts = re.search(r"([A-Z]*)([0-9]*)", booster_url_specifier)
    booster = booster_parts.group(1) + str(int(booster_parts.group(2)))

    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    products = soup.find_all("div", {"class": "card-product"})
    prices = {}

    for product in products:
      id = product.find("span").text

      pricestrong = product.find("strong").text
      pricefilter = filter(str.isdigit, pricestrong)
      pricestr = "".join(pricefilter)
      price = int(pricestr)

      if not id in prices:
        prices[id] = [price]
      else:
        prices[id].append(price)

    for id in prices:
      prices[id].sort()
      for para_id, price in enumerate(prices[id]):
        self.add_card(id, price, para_id, booster)

  def register_card(self, card_id):
    if not card_id in self.price_dict:
      if card_id in self.ref_dict:
        self.price_dict[card_id] = self.ref_dict[card_id].copy()
      else:
        logging.warn(
            "YYTDigiScraper, register_card, price entry found with no name")
        self.price_dict[card_id] = digimoncard.new_card_entry("UNKNOWN")

  def add_card(self, card_id: str, price: int, alt_id=1, booster_source=""):
    if not card_id in self.price_dict:
      self.register_card(card_id)

    if booster_source == "" or booster_source.upper() in card_id.upper():
      cluster = self.price_dict[card_id]["main_variant"]
      variant_id = f"p{alt_id}"
      cluster[variant_id] = price
    else:
      cluster = self.price_dict[card_id]["alt_variant"]
      variant_id = f"{booster_source}-p{alt_id}"
      cluster[variant_id] = price

    logging.info(f"{card_id}: {self.price_dict[card_id]}")
    return
