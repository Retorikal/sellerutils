import requests
import bs4
import re
import logging

from fetcher.cardnames import digimoncard

from fetcher.price.IScraper import IScraper


class ScraperBigwebDigi(IScraper):
  def __init__(self) -> None:
    self.domain = "https://yuyu-tei.jp/"
    self.digi_url = "https://yuyu-tei.jp/game_digi/"
    self.price_dict = {}
    self.ref_dict = {}
    super().__init__()

  def scrape_update(self, price_dict: dict):
    self.ref_dict = digimoncard.get_cardname_dict()
    self.price_dict = price_dict

    cats = self.get_categories()
    promo_cats = [cat for cat in cats if "promo" in cat]
    regular_cats = [cat for cat in cats if not "promo" in cat]

    for cat in regular_cats:
      self.scrape_prices_regular(cat)

    for cat in promo_cats:
      self.scrape_prices_promo(cat)

    self.ref_dict.clear()

  def get_categories(self):
    logging.info("get_categories start")
    page = requests.get(self.digi_url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    singles = soup.find("li", {"class": "item_single_card"})
    categories = singles.find_all("a", href=True)
    links = [category["href"] for category in categories]
    print(f"{len(links)} links found")

    seen = set()
    return [self.domain + link for link in links if not (link in seen or seen.add(link))]

  def scrape_prices_promo(self, url: str):
    logging.info(f"scrape_prices_promo start, scraping from {url}")
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    groups = soup.find_all(
        "div", {"class": re.compile("group_box")})
    para_count = {}

    for group in groups:
      ids_p = group.find_all('p', {'class': 'id'})
      prices_p = group.find_all('p', {'class': 'price'})

      for id_p, price_p in zip(ids_p, prices_p):
        id = id_p.text.strip()
        para_count[id] = para_count[id] + 1 if id in para_count else 0
        price = int(price_p.text.split()[0][:-1])
        self.add_card(id, price, para_count[id], "P")

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
    para_count = {}

    for group in [*groups_base, *groups_para]:
      ids_p = group.find_all('p', {'class': 'id'})
      prices_p = group.find_all('p', {'class': 'price'})

      for id_p, price_p in zip(ids_p, prices_p):
        id = id_p.text.strip()
        price = int(price_p.text.split()[0][:-1])
        para_count[id] = para_count[id] + 1 if id in para_count else 0
        self.add_card(id, price, para_count[id], booster)

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
