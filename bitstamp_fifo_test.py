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
        expected = 2000-2000-10-10
        self.assertEqual(gain, expected)

    def test_different_year(self):
        gain = process_transactions(
            'sample_transactions/same_sale.csv', {}, '2019')
        self.assertEqual(gain, 0)

    def test_sale_half_price(self):
        gain = process_transactions(
            'sample_transactions/sale_half_price.csv', {}, '2018')
        expected = 1000-10-2000-10
        self.assertEqual(gain, expected)

    def test_sale_half_holding(self):
        gain = process_transactions(
            'sample_transactions/sale_half_holding.csv', {}, '2018')
        expected = 1000-10-1000-5
        self.assertEqual(gain, expected)

    def test_sale_mixed_holding(self):
        gain = process_transactions(
            'sample_transactions/sale_mixed_holding.csv', {}, '2018')
        first_sale = 8000-10-1000-10-2000-5
        second_sale = 8000-10-2000-5
        self.assertEqual(gain, first_sale+second_sale)

    def test_sale_mixed_year_holding(self):
        gain = process_transactions(
            'sample_transactions/sale_mixed_year_holding.csv', {}, '2019')
        sale = 8000-10-2000-5
        self.assertEqual(gain, sale)


if __name__ == '__main__':
    unittest.main()
