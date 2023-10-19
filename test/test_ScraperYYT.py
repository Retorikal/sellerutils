import unittest
import logging
from fetcher.price.ScraperYYT import ScraperYYTDigi as sc


class TestScraperYYT(unittest.TestCase):

  @classmethod
  def setUpClass(self):
    self.scraper = sc()

  def test_get_categories(self):
    cats = self.scraper.get_categories()
    print(cats)
    self.assertGreater(len(cats), 10)

  def test_get_prices_regular(self):
    self.scraper.scrape_prices_regular(
      "https://yuyu-tei.jp/sell/digi/s/bt15")
    print(self.scraper.price_dict)
    self.assertGreater(len(self.scraper.price_dict), 1)
    pass

  def test_get_prices_promo(self):
    self.scraper.scrape_prices_promo(
      "https://yuyu-tei.jp/sell/digi/s/promo-bt10")
    print(self.scraper.price_dict)
    self.assertGreater(len(self.scraper.price_dict), 1)
    pass


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  logging.info("testing start")
  unittest.main()
