#!/usr/bin/env python3

from database.Card import CardDB
from database.Stocks import StockDB
from factory.image.SVG import SVGGenerator
from factory.uploadfile.Tokopedia import TokopediaGenerator
from fetcher.price.IScraper import IScraper
from fetcher.price.YYT import YYTScraper

import os
import argparse
import logging
import configs
import csv


def sanitize_io_args():
  if not args.input:
    raise Exception("Input required (-i)")
  if not args.output:
    stockid = args.input.split("/")[-1].split(".")[0]
    args.output = f"{stockid}.xlsx"


logging.basicConfig(level=logging.INFO)

if not os.path.exists(configs.user_config):
  logging.info("Creating user directory")
  os.mkdir(configs.user_config)

prices = CardDB(configs.db_path())
parser = argparse.ArgumentParser(
    description='Utility to manage Retorikal TCG Shop',
    epilog='Copyright 2024 Reinard Rahardian')

parser.add_argument('operation', help="Operation to do: 'generate' uploadable excel, 'update' excel prices, 'refetch' price database, or 'draw' product image, or 'tag' variant name",
                    choices=["generate", "update", "refetch", "draw", "tag"])
parser.add_argument('-s', '--source', nargs='?', required=False,
                    choices=["yuyutei", "bigweb"], default="yuyutei")
parser.add_argument('-i', '--input', nargs='?', required=False)
parser.add_argument('-o', '--output', nargs='?', required=False)

args = parser.parse_args()

match args.operation:
  case "generate":
    sanitize_io_args()
    tokped_generator = TokopediaGenerator()
    stocks = StockDB(args.input, prices)
    tokped_generator.generate_from_new_stock(stocks, args.output)
    logging.info(f"Generated uploadable written at {args.output}")

  case "update":
    sanitize_io_args()
    tokped_generator = TokopediaGenerator(args.input)
    tokped_generator.update_prices(prices, args.output)
    logging.info(f"Updated uploadable written at {args.output}")

  case "refetch":
    source = IScraper()
    match args.source:
      case "yuyutei":
        source = YYTScraper()

    prices.refresh(source, True)

    logging.info("Successfully updated the pricelist.")

  case "draw":
    sanitize_io_args()
    logging.info("To Be Implemented")


# stockpath = "workspace/input/ragnaloard.csv"
# stockid = stockpath.split("/")[-1].split(".")[0]
# pricespath = "workspace/db/nameprices.json"
# tokopediapath = f"workspace/output/{stockid}.xlsx"

# tokopedia = Tokopedia(tokopediapath)
# stocks = Stocks(stockpath, pricespath)
# tokopedia.create_uploadable_from_new_stock(stocks)

# tokopedia = Tokopedia(f"workspace/output/refresh.xlsx",
#                       "workspace/input/ubah-sekaligus-15995836-(1)-20231223154004.414.xlsx")
# stocks = Stocks("", "workspace/db/nameprices.json")

# tokopedia.create_uploadable_from_old_stock(stocks)
