import unittest
from argparse import ArgumentTypeError
from home_store.cmdtool import check_period


class CmdToolTest(unittest.TestCase):

    def test_check_period_valid_date(self):
        full_date = check_period('2022-12-12')
        self.assertEqual(type(full_date), str)
        year_month = check_period('2022-12')
        self.assertEqual(type(year_month), str)

    def test_check_invalid_type(self):
        self.assertRaises(ArgumentTypeError, check_period, '123')


if __name__ == '__main__':
    unittest.main()
