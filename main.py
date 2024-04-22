
from database.Price import Prices
from database.Stocks import Stocks
from factory.image.SVGTemplate import SVGTemplate
from factory.uploadfile.Tokopedia import Tokopedia

import logging
import csv

logging.basicConfig(level=logging.INFO)

stockpath = "workspace/input/ipm.csv"
stockid = stockpath.split("/")[-1].split(".")[0]
pricespath = "workspace/db/nameprices.json"
tokopediapath = f"workspace/output/{stockid}.xlsx"

tokopedia = Tokopedia(tokopediapath)
stocks = Stocks(stockpath, pricespath)
tokopedia.create_uploadable_from_new_stock(stocks)

# tokopedia = Tokopedia(f"workspace/output/refresh.xlsx",
#                       "workspace/input/ubah-sekaligus-15995836-(1)-20231223154004.414.xlsx")
# stocks = Stocks("", "workspace/db/nameprices.json")

# tokopedia.create_uploadable_from_old_stock(stocks)
