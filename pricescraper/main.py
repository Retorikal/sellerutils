import PriceDB
import yuyutei
import digimoncard
import re
import logging

logging.basicConfig(level=logging.INFO)

name_dict = digimoncard.get_cardname_dict(url="")
db = PriceDB.PriceDB(name_dict)
yuyutei.scrape(db)

db.dump("img_prices.json")
