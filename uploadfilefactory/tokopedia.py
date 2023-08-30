import openpyxl as opxl
import os

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


class Tokopedia():
  def __init__(self, filename, template=""):
    self.filename = filename
    self.filesrc = template
    self.entry_ws = self.wb.get_sheet_by_name("ISI Template Impor Produk")

    if os.path.exists(template):
      self.wb = opxl.load_workbook(template)
    else:
      raise FileNotFoundError

  def add_entry(self, to_append):
    self.entry_ws.append(to_append)

  def save(self):
    self.wb.save(self.filename)

  pass
