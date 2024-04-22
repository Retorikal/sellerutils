from typing import Any, Callable
import openpyxl as opxl
from openpyxl.worksheet.table import Table
from database.Price import Prices as Prices
import os
import json
from string import Template

from database.Stocks import Stocks
from factory.image.SVGTemplate import SVGTemplate

columns = [
  "Pesan Error",
  "Nama Produk",
  "Deskripsi Produk",
  "Kode Kategori",
  "Berat (Gram)",
  "Minimum Pemesanan",
  "Nomor Etalase",
  "Waktu Proses Preorder",
  "Kondisi",
  "Foto Produk 1",
  "Foto Produk 2",
  "Foto Produk 3",
  "Foto Produk 4",
  "Foto Produk 5",
  "URL Video Produk 1",
  "URL Video Produk 2",
  "URL Video Produk 3",
  "SKU Name",
  "Status",
  "Jumlah Stok",
  "Harga (Rp)",
  "Kurir Pengiriman",
  "Asuransi Pengiriman"
]


default_name = "workspace/static/tambah-sekaligus.xlsx"
default_fields_path = "workspace/static/productdescdefaults.json"
templatepath = "workspace/static/templates/templateDigi.svg"


class Tokopedia():
  def __init__(self, workpath, xlspath=default_name):
    self.workpath = workpath
    self.imgfactory = SVGTemplate(templatepath)

    if os.path.exists(xlspath):
      self.wb = opxl.load_workbook(xlspath)
    else:
      raise FileNotFoundError

    with (open(default_fields_path)) as defaults_file:
      self.defaults = json.load(defaults_file)

    for key in self.defaults:
      if type(self.defaults[key]) is list:
        self.defaults[key] = "\n".join(self.defaults[key])

      if "$" in self.defaults[key]:
        self.defaults[key] = Template(self.defaults[key])

  def create_uploadable_from_new_stock(self, stocks: Stocks):
    self.entry_ws = self.wb["ISI Template Impor Produk"]
    for stock in stocks.parse_stock():
      self.__populate_from_stock_entry(stock)
      self.imgfactory.generate_from_stock_entry(stock)
    self.save()
    self.imgfactory.dump_results()

  def create_uploadable_from_old_stock(self, stocks: Stocks):
    self.entry_ws = self.wb["Ubah - Informasi Penjualan"]
    column_sku = 11
    column_price = 8
    row = 4
    while True:
      sku = self.entry_ws.cell(row, column_sku)
      price = self.entry_ws.cell(row, column_price)

      if sku.value is None or str(price.value)[-3:] != "000":
        break

      price.value = str(stocks.prices.get_price(str(sku.value)) * stocks.rate)
      row += 1

    self.wb.save(self.workpath)

  def __populate_from_stock_entry(self, stock):
    """
    Accepts `card_details` adds an appropriate entry to the Tokopedia uploadable xls.
    @param `card_details`: a dict with the following format:
    ```
    dict{\
      "CARDCODE": # Card's full code qualifier plus parallel notation, ex: BT11-023_P1,
      "CARDNAME": # Card's full name,
      "TITLEDESC": # Inline short description,
      "CARDDESC": # Full string for product description in shop listing,
      "PRICE": # Price in idr: yyt * 100,
      "STOCK": # Amount of card in stock,
      "CARDSKU": # Card image filename
    }
    ```
    """
    row = []
    for column in columns:
      value = self.defaults.get(column, "")

      if type(value) is Template:
        value = value.substitute(stock)

      row.append(value)
    self.entry_ws.append(row)

  def save(self):
    self.wb.save(self.workpath)
