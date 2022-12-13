import unittest
from home_store.helpers import populate
from home_store.models import Sensor


class PopulateTest(unittest.TestCase):

    def test_create_sensor(self):
        sensor = populate.create_sensor('yada', '2022-12-12')
        self.assertEqual(type(sensor), Sensor)
        self.assertEqual(sensor.name, 'yada')

    @unittest.skip
    def test_create_for_date(self):
        sensors = populate.create_for_day('tmp', '2022-12-12', 10)
        self.assertEqual(len(sensors), 10)

    def test_get_int_tuple(self):
        year, month = populate.get_int_tuple('2022-09')
        self.assertEqual(year, 2022)
        self.assertEqual(month, 9)

if __name__ == '__main__':
    unittest.main()
