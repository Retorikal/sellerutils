import json
from string import Template

defaults_file_path = "./productdescdefaults.json"
columns = [
    "",
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


defaults = {}


def load_defaults():
  with (open(defaults_file_path)) as defaults_file:
    defaults = json.load(defaults_file)

  for key in defaults:
    if defaults[key] is list:
      defaults[key] = defaults[key].join("\n")

    if "$" in defaults[key]:
      defaults[key] = Template(defaults[key])


def create_entry(info):
  row = []
  for column in columns:
    value = defaults.get(column, "")
    if value is Template:
      value = value.substitute(info)
    row.append(value)

    pass

  return row
