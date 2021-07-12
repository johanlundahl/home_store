import unittest
from home_store.models import Sensor


class TestSensor(unittest.TestCase):

    def test_not_valid_create(self):
        invalid = {'name': 'yalla', 'temperature': 12}
        self.assertFalse(Sensor.valid_create(invalid))
        invalid = {'name': 'yalla', 'temperature': 12, 'humidity': 15}
        self.assertFalse(Sensor.valid_create(invalid))

    def test_valid_create(self):
        valid = {'name': 'yalla', 'temperature': 12,
                 'humidity': 15, 'timestamp': 123}
        self.assertTrue(Sensor.valid_create(valid))

    def test_not_valid_update(self):
        invalid = {'number': 'yalla', 'another': 55}
        self.assertFalse(Sensor.valid_update(invalid))

    def test_valid_update(self):
        valid = {'name': 'yalla', 'temperature': 12,
                 'humidity': 15, 'timestamp': 123}
        self.assertTrue(Sensor.valid_update(valid))

    def test_valid_update_with_new_state(self):
        valid = {'name': 'yalla', 'temperature': 12, 'humidity': 15,
                 'new_state': 'bla', 'timestamp': 123}
        self.assertTrue(Sensor.valid_update(valid))

    def test_create(self):
        valid = {'name': 'yalla', 'temperature': 12, 'humidity': 15,
                 'timestamp': '2021-01-03 22:06:10'}
        sensor = Sensor.create(valid)
        self.assertTrue(isinstance(sensor, Sensor))
        self.assertEqual('yalla', sensor.name)


if __name__ == '__main__':
    unittest.main()
