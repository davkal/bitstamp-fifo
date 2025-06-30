import unittest
from bitstamp_fifo import process_transactions


class TestFifo(unittest.TestCase):

    def test_none(self):
        gain = process_transactions('sample_transactions/none.csv', {}, '2018')
        self.assertEqual(gain, 0)

    def test_no_sale(self):
        gain = process_transactions(
            'sample_transactions/no_sale.csv', {}, '2018')
        self.assertEqual(gain, 0)

    def test_same_sale(self):
        gain = process_transactions(
            'sample_transactions/same_sale.csv', {}, '2018')
        expected = 2000-2000  # No fees in new format
        self.assertEqual(gain, expected)

    def test_different_year(self):
        gain = process_transactions(
            'sample_transactions/same_sale.csv', {}, '2019')
        self.assertEqual(gain, 0)

    def test_sale_half_price(self):
        gain = process_transactions(
            'sample_transactions/sale_half_price.csv', {}, '2018')
        expected = 1000-2000  # No fees in new format
        self.assertEqual(gain, expected)

    def test_sale_half_holding(self):
        gain = process_transactions(
            'sample_transactions/sale_half_holding.csv', {}, '2018')
        expected = 1000-1000  # No fees in new format
        self.assertEqual(gain, expected)

    def test_sale_mixed_holding(self):
        gain = process_transactions(
            'sample_transactions/sale_mixed_holding.csv', {}, '2018')
        # First sale: 2.0 BTC at 4000 EUR each (8000 total) - uses 1.0 at 1000 + 1.0 at 2000 = 3000 cost
        # Second sale: 0.5 BTC at 8000 EUR each (4000 total) - uses 0.5 at 2000 = 1000 cost  
        # Third sale: 0.5 BTC at 8000 EUR each (4000 total) - uses 0.5 at 2000 = 1000 cost
        first_sale = 8000-3000
        second_sale = 4000-1000
        third_sale = 4000-1000
        self.assertEqual(gain, first_sale+second_sale+third_sale)

    def test_sale_mixed_year_holding(self):
        gain = process_transactions(
            'sample_transactions/sale_mixed_year_holding.csv', {}, '2019')
        # Sell 1.0 BTC at 8000 EUR in 2019 - uses first 1.0 BTC at 1000 cost
        sale = 8000-1000
        self.assertEqual(gain, sale)


if __name__ == '__main__':
    unittest.main()
