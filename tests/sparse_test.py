import unittest
from home_store.helpers import sparse
from home_store.models import Sensor
from home_store.app import app, mydb
from flask_testing import TestCase
from datetime import datetime, timedelta


class PopulateTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        return app

    def setUp(self):
        mydb.create_all()
        self.client = app.test_client()

    def tearDown(self):
        mydb.session.remove()
        mydb.drop_all()

    def test_get_int_tuple(self):
        year, month = sparse.get_int_tuple('2022-09')
        self.assertEqual(year, 2022)
        self.assertEqual(month, 9)

    def test_sparse_records_for_one_hour(self):
        dt = datetime.strptime('2022-12-20 11:15:03', '%Y-%m-%d %H:%M:%S')
        s1 = Sensor('tmp', 10, 20, dt+timedelta(minutes=1))
        s2 = Sensor('tmp', 11, 21, dt+timedelta(minutes=0))
        s3 = Sensor('tmp', 12, 22, dt+timedelta(minutes=2))
        s4 = Sensor('tmp', 13, 23, dt+timedelta(minutes=3))
        sensors = [s1, s2, s3, s4]
        sparsed = sparse.sparse_records(sensors)
        self.assertEqual(len(sparsed), 3)
        self.assertTrue(s2 not in sparsed)

    def test_sensor_records(self):
        dt = datetime.strptime('2022-12-20 11:15:03', '%Y-%m-%d %H:%M:%S')
        sensors = []
        sensors.append(Sensor('A', 10, 20, dt+timedelta(hours=2)))
        sensors.append(Sensor('A', 20, 30, dt+timedelta(hours=1)))
        sensors.append(Sensor('A', 30, 40, dt+timedelta(days=1)))
        with mydb:
            for sensor in sensors:
                mydb.add(sensor)
        self.assertEqual(len(sparse.sensor_records('A', dt)), 2)

    def test_remove_records(self):
        dt = datetime.strptime('2022-12-20 11:15:03', '%Y-%m-%d %H:%M:%S')
        sensors = []
        sensors.append(Sensor('B', 10, 20, dt+timedelta(hours=2)))
        sensors.append(Sensor('B', 20, 30, dt+timedelta(hours=1)))
        sensors.append(Sensor('AB', 30, 40, dt+timedelta(days=2)))
        with mydb:
            for sensor in sensors:
                mydb.add(sensor)
        sparse.remove_records(sensors)
        self.assertEqual(len(sparse.sensor_records('B', dt)), 0)


if __name__ == '__main__':
    unittest.main()
