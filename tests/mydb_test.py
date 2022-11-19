from datetime import datetime
import unittest
from flask_testing import TestCase
from home_store.models import Sensor, Panel
from home_store.app import app, mydb


class TestMyDB(TestCase):

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

    def test_empty_db(self):
        with mydb:
            sensors = mydb.sensors()
            self.assertTrue(len(sensors) == 0)

    def test_add_a_sensor(self):
        sensor = Sensor('fake', 12.0, 55.5, datetime.now())
        with mydb:
            mydb.add(sensor)
            db_sensor = mydb.latest_sensor('fake')
            self.assertEqual(sensor, db_sensor)

    def test_sensor_max(self):
        pass

    def test_sensors_something_something(self):
        pass

    def test_panels(self):
        with mydb:
            mydb.add(Panel(12, 'test', 12, True, 50))
            mydb.add(Panel(13, 'test', 13, True, 51))
            mydb.add(Panel(12, 'test', 13, False, 52))
            self.assertEqual(len(mydb.panels()), 2)

    def test_panel_of_same_id(self):
        with mydb:
            mydb.add(Panel(21, 'test1', 12, True, 50))
            mydb.add(Panel(21, 'test1', 13, True, 51))
            mydb.add(Panel(11, 'test2', 13, False, 52))

            panels = mydb.panel(21)
            self.assertEqual(len(panels), 2)
            self.assertEqual(panels[0].name, 'test1')

    def test_panel_with_sort_page_size(self):
        with mydb:
            mydb.add(Panel(21, 'tmp', 12, True, 25))
            mydb.add(Panel(21, 'tmp', 13, True, 30))
            mydb.add(Panel(21, 'tmp', 14, False, 35))

            panels = mydb.panel(21, limit=1, sort='asc')
            self.assertEqual(len(panels), 1)
            self.assertEqual(panels[0].name, 'tmp')
            self.assertEqual(panels[0].energy, 12)

            panels = mydb.panel(21, limit=1, sort='desc')
            self.assertEqual(len(panels), 1)
            self.assertEqual(panels[0].energy, 14)


if __name__ == '__main__':
    unittest.main()
