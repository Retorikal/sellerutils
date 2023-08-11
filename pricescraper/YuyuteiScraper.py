import requests
import bs4
import re
import logging

from pricescraper.PriceDB import PriceDB
from pricescraper.Scraper import Scraper


class YuyuteiScraper(Scraper):
  def __init__(self) -> None:
    self.base_url = "https://yuyu-tei.jp/"
    self.digi_url = "/game_digi/"
    self.price_dict = {}
    super().__init__()

  def scrape(self, price_dict: dict):
    cats = self.get_categories(self.base_url + self.digi_url, self.base_url)
    self.price_dict = price_dict
    promo_cats = [cat for cat in cats if "promo" in cat]
    regular_cats = [cat for cat in cats if not "promo" in cat]

    for cat in regular_cats:
      self.scrape_prices_regular(cat)

    for cat in promo_cats:
      self.scrape_prices_promo(cat)

  def get_categories(self, url, base_url):
    logging.info("get_categories start")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    singles = soup.find("li", {"class": "item_single_card"})
    categories = singles.find_all("a", href=True)
    links = [category["href"] for category in categories]
    print(f"{len(links)} links found")

    seen = set()
    return [base_url + link for link in links if not (link in seen or seen.add(link))]

  def scrape_prices_promo(self, url: str):
    logging.info(f"scrape_prices_promo start, scraping from {url}")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    groups = soup.find_all(
        "div", {"class": re.compile("group_box")})

    for group in groups:
      ids_p = group.find_all('p', {'class': 'id'})
      prices_p = group.find_all('p', {'class': 'price'})
      consequent = 0
      last_id = ""

      for id_p, price_p in zip(ids_p, prices_p):
        id = id_p.text.strip()
        price = int(price_p.text.split()[0][:-1])
        consequent = consequent + 1 if last_id == id else 0
        last_id = id
        self.add_card(id, price, consequent, "P")

  def scrape_prices_regular(self, url: str):
    logging.info(f"scrape_prices_regular start, scraping from {url}")
    booster_url_specifier = url.split("?")[-1][4:].upper()
    result = re.search(r"([A-Z]*)([0-9]*)", booster_url_specifier)
    booster = result.group(1) + str(int(result.group(2)))

    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    groups_para = soup.find_all(
        "div", {"class": re.compile("group_box rarity_P")})
    groups_base = soup.find_all(
        "div", {"class": re.compile("group_box rarity_[^P]")})

    for group in [*groups_base, *groups_para]:
      ids_p = group.find_all('p', {'class': 'id'})
      prices_p = group.find_all('p', {'class': 'price'})
      consequent = 0
      last_id = ""

      for id_p, price_p in zip(ids_p, prices_p):
        id = id_p.text.strip()
        price = int(price_p.text.split()[0][:-1])
        consequent = consequent + 1 if last_id == id else 0
        last_id = id
        self.add_card(id, price, consequent, booster)

  def register_card(self, card_id):
    if not card_id in self.price_dict:
      self.price_dict[card_id] = {
        "name": card_id,
        "variants": 0,
        "main_variant": {},
        "alt_variant": {},
      }
      # Probably need to move this declaration somewhere

  def add_card(self, card_id: str, price: int, consequent=1, booster_source=""):
    if not card_id in self.price_dict:
      self.register_card(card_id)

    if booster_source == "" or booster_source.upper() in card_id.upper():
      cluster = self.price_dict[card_id]["main_variant"]
      size = len(cluster)
      variant_id = f"p{size}"
      cluster[variant_id] = price
    else:
      cluster = self.price_dict[card_id]["alt_variant"]
      variant_id = f"{booster_source}-p{consequent}"
      if variant_id in cluster:
        cluster[variant_id] = price
      else:
        cluster[f"_{variant_id}"] = price

    logging.info(f"{card_id}: {self.price_dict[card_id]}")
    return
