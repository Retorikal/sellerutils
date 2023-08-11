import requests
import bs4
import re
import PriceDB
import logging

yuyutei_digi_url = "/game_digi/"
yuyutei_base_url = "https://yuyu-tei.jp/"


def scrape(price_db: PriceDB.PriceDB, base_url=yuyutei_base_url, digi_url=yuyutei_digi_url):
  cats = get_categories(base_url + digi_url, base_url)
  promo_cats = [cat for cat in cats if "promo" in cat]
  regular_cats = [cat for cat in cats if not "promo" in cat]

  for cat in regular_cats:
    scrape_prices_regular(price_db, cat)

  for cat in promo_cats:
    scrape_prices_promo(price_db, cat)


def get_categories(url, base_url):
  logging.info("get_categories start")
  page = requests.get(url)
  soup = bs4.BeautifulSoup(page.content, "html.parser")
  singles = soup.find("li", {"class": "item_single_card"})
  categories = singles.find_all("a", href=True)
  links = [category["href"] for category in categories]
  print(f"{len(links)} links found")

  seen = set()
  return [base_url + link for link in links if not (link in seen or seen.add(link))]


def scrape_prices_promo(prices_db: PriceDB.PriceDB, url: str):
  logging.info(f"Scraping from {url}")
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
      prices_db.add_card(id, price, consequent, "P")


def scrape_prices_regular(prices_db: PriceDB.PriceDB, url: str):
  logging.info(f"Scraping from {url}")
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
      prices_db.add_card(id, price, consequent, booster)
