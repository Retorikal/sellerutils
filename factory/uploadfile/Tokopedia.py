from typing import Any
import openpyxl as opxl
from database.Price import Prices as Prices
import os
import json
from string import Template

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


class Tokopedia():
  def __init__(self, workpath, templatepath=default_name):
    self.workpath = workpath

    if os.path.exists(templatepath):
      self.wb = opxl.load_workbook(templatepath)
    else:
      raise FileNotFoundError

    self.entry_ws = self.wb.get_sheet_by_name("ISI Template Impor Produk")

    with (open(default_fields_path)) as defaults_file:
      self.defaults = json.load(defaults_file)

    for key in self.defaults:
      if type(self.defaults[key]) is list:
        self.defaults[key] = "\n".join(self.defaults[key])

      if "$" in self.defaults[key]:
        self.defaults[key] = Template(self.defaults[key])

  def populate_from_stock_entry(self, info):
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
      "CARDIMG": # Card image filename
    }
    ```
    """
    row = []
    for column in columns:
      value = self.defaults.get(column, "")

      if type(value) is Template:
        value = value.substitute(info)

      row.append(value)
    self.entry_ws.append(row)

  def save(self):
    self.wb.save(self.workpath)
