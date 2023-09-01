import openpyxl as opxl
from pricefetcher.PriceDB import PriceDB as PDB
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


default_name = "static/tambah-sekaligus.xlsx"
defaults_file_path = "./productdescdefaults.json"


class Tokopedia():
  def __init__(self, filename, template=""):
    self.filename = filename
    self.filesrc = template
    self.entry_ws = self.wb.get_sheet_by_name("ISI Template Impor Produk")

    if os.path.exists(template):
      self.wb = opxl.load_workbook(template)
    else:
      raise FileNotFoundError

    with (open(defaults_file_path)) as defaults_file:
      self.defaults = json.load(defaults_file)

    for key in self.defaults:
      if self.defaults[key] is list:
        self.defaults[key] = self.defaults[key].join("\n")

      if "$" in self.defaults[key]:
        self.defaults[key] = Template(self.defaults[key])

  def populate_from_stock_file(self, db: PDB, stocks):
    for stock in stocks:
      self.entry_ws.append(self.create_entry(stock))

  def create_entry(self, info):
    row = []
    for column in columns:
      value = self.defaults.get(column, "")
      if value is Template:
        value = value.substitute(info)
      row.append(value)
    return row

  def save(self):
    self.wb.save(self.filename)
