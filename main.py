
from database.Price import Prices
from database.Stocks import Stocks
from factory.image.SVGTemplate import SVGTemplate
from factory.uploadfile.Tokopedia import Tokopedia

import logging
import csv

logging.basicConfig(level=logging.INFO)

stockpath = "workspace/input/2023-12-2.csv"
stockid = stockpath.split("/")[-1].split(".")[0]

pricespath = "workspace/db/nameprices.json"
templatepath = "workspace/static/templates/templateDigi.svg"
tokopediapath = f"workspace/output/{stockid}.xlsx"

imgfactory = SVGTemplate(templatepath)
tokopedia = Tokopedia(tokopediapath)
stocks = Stocks(stockpath, pricespath)

for stock in stocks.parse_stock():
  imgfactory.generate_from_stock_entry(stock)
  tokopedia.populate_from_stock_entry(stock)

imgfactory.dump_results()
tokopedia.save()
