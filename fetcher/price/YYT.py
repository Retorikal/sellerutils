import requests
import bs4
import re
import logging

from fetcher.cardnames import digimoncard
from fetcher.price.IScraper import IScraper


class YYTScraper(IScraper):
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
      try:
        self.scrape_prices_regular(cat)
      except Exception as error:
        logging.warn(f"Unable to scrape category {cat}", error)

    for cat in promo_cats:
      try:
        self.scrape_prices_promo(cat)
      except Exception as error:
        logging.warn(f"Unable to scrape promo category {cat}", error)

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
    logging.info(f"YYTScraper.scrape_prices_promo: scraping {url}")
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

      try:
        self.add_card(id, price, para_count[id], "P")
      except Exception as error:
        logging.warn(
          f"YYTSCraper.scrape_prices_promo failed adding {id}", error)

  def scrape_prices_regular(self, url: str):
    logging.info(f"YYTScraper.scrape_prices_regular: scraping {url}")
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
        try:
          self.add_card(id, price, para_id, booster)
        except Exception as error:
          logging.warn(
            f"YYTSCraper.scrape_prices_regular failed adding {id}", error)

  def get_create_card_dict(self, card_id):
    if not card_id in self.price_dict:
      if card_id in self.ref_dict:
        self.price_dict[card_id] = self.ref_dict[card_id].copy()
      else:
        logging.warn(f"YYTScraper.register_card: {card_id} name not found")
        self.price_dict[card_id] = digimoncard.new_card_entry("UNKNOWN")

    return self.price_dict[card_id]

  def add_card(self, card_id: str, price: int, alt_id=1, booster_source=""):
    card_dict = self.get_create_card_dict(card_id)

    variant_text = []

    # Add identifier
    if booster_source == "" or booster_source.upper() in card_id.upper():
      variant_id = f"p{alt_id}"
    else:
      variant_id = f"{booster_source}-p{alt_id}"

      if booster_source == "P":
        card_dict["varnames"][variant_id] = "Promo"
      else:
        card_dict["varnames"][variant_id] = f"{booster_source} reprint"

    if alt_id > 0:
      variant_text.append(f"Alternate {alt_id}")

    if not variant_id in card_dict["varnames"]:
      card_dict["varnames"][variant_id] = " ".join(variant_text)

    card_dict["variants"][variant_id] = price
