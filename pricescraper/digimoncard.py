import requests
import bs4
import re
import PriceDB
import logging

digimoncard_url = "https://en.digimoncard.com/cardlist/index.php?search=true"
test_file = "pricescraper/digimoncard.html"


def get_cardname_dict(url=digimoncard_url):
  logging.info("Getting cardname dict")
  card_dict = {}
  soup = None
  if url != "":
    page = requests.post(url, data={"free": ""})
    soup = bs4.BeautifulSoup(page.content, "html.parser")
  else:
    logging.info("Empty URL, parsing test file")
    soup = bs4.BeautifulSoup(
        open(test_file).read(), "html.parser")

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
      card_dict[card_id] = {
        "name": card_name,
        "variants": 1,
        "main_variant": {},
        "alt_variant": {},
      }
    # Probably need to move this declaration somewhere

    else:
      card_dict[card_id]["variants"] += 1

  return card_dict
