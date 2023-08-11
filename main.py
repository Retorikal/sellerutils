import csv


def add_stocks(stocks, prices):
  pass


def parse_stocks(filepath):
  stock_dict = {}
  with open(filepath) as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)
    for row in reader:
      stock_dict[row[0]] = [int(i) for i in row[1:] if i != '']

  return stock_dict


stocks = parse_stocks("stock.csv")

print(stocks)
