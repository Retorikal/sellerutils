import requests
import bs4
import re
import logging
import os

digimoncard_url = "https://en.digimoncard.com/cardlist/index.php?search=true"
test_file = os.path.join(os.getcwd(), "workspace/static/digimoncard.html")


def new_card_entry(name):
  return {
      "name": name,
      "variants": [],
      "images": {},
      "prices": {},
      "varnames": {}
  }


def get_cardname_dict(url=digimoncard_url, file=""):
  logging.info("Getting cardname dict")
  card_dict = {}
  soup = None
  if url != "":
    page = requests.post(url, data={"free": ""})
    soup = bs4.BeautifulSoup(page.content, "html.parser")
  else:
    logging.info("Empty URL, parsing test file")
    soup = bs4.BeautifulSoup(
        open(file).read(), "html.parser")

  logging.info("Soup created")

  card_name_divs = soup.find_all('div', {'class': 'card_name'})
  cardinfo_top_divs = soup.find_all('div', {'class': 'card_img'})

  logging.info("Get finished, parsing")
  for cardname_div, cardinfo_top_div in zip(card_name_divs, cardinfo_top_divs):
    card_name = cardname_div.text
    card_img_url = cardinfo_top_div.find("img")["src"]
    card_img_name = card_img_url.split("/")[-1]
    card_id = re.split('_|\.', card_img_name)[0]

    if not card_id in card_dict:
      card_dict[card_id] = new_card_entry(card_name)

  return card_dict
