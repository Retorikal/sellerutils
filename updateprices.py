from database.Price import Prices
from database.Stocks import Stocks
from factory.image.SVGTemplate import SVGTemplate
from factory.uploadfile.Tokopedia import Tokopedia
from fetcher.price.ScraperYYT import ScraperYYTDigi as sc

import logging
import csv

logging.basicConfig(level=logging.INFO)


pricespath = "workspace/db/nameprices.json"

db = Prices(pricespath)

db.refresh_prices(sc(), True)
