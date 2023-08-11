import PriceDB
import pricescraper.YuyuteiScraper as YuyuteiScraper
import digimoncard
import logging

logging.basicConfig(level=logging.INFO)

name_dict = digimoncard.get_cardname_dict(url="")
db = PriceDB.PriceDB(name_dict)
YuyuteiScraper.scrape(db)

db.dump("img_prices.json")
