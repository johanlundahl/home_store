import unittest
from flask_testing import TestCase
from home_store.app import app, mydb

class IntegrationTest(TestCase):

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

    def test_root(self):
        response = self.client.get('/api/v2', headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        
    def test_status(self):
        response = self.client.get('/api/v2/status', headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        self.assertIn('size', response.json)
        self.assertIn('count', response.json)
        self.assertIn('oldest', response.json)
        self.assertIn('newest', response.json)

    def test_get_sensors(self):
        response = self.client.get('/api/v2/sensors/indoor')
        self.assertEqual(404, response.status_code)
        data = {
            "name": "indoor",
            "temperature": 20,
            "humidity": 50,
            "timestamp": "2020-11-20 11:14:03"
        }
        response = self.client.post('/api/v2/sensors', json=data)
        response = self.client.get('/api/v2/sensors')
        self.assertEqual(200, response.status_code)
        response = self.client.get('/api/v2/sensors/indoor')
        self.assertEqual(200, response.status_code)

    def test_get_several_sensors(self):
        data = {
            "name": "indoor",
            "temperature": 20,
            "humidity": 50,
            "timestamp": "2020-11-20 11:14:03"
        }
        self.client.post('/api/v2/sensors', json=data)
        data = {
            "name": "outdoor",
            "temperature": 5,
            "humidity": 65,
            "timestamp": "2020-11-20 11:14:03"
        }
        self.client.post('/api/v2/sensors', json=data)
        response = self.client.get('/api/v2/sensors')
        result = [x['name'] in ['outdoor', 'indoor'] for x in response.json]
        self.assertTrue(all(result))

    def test_add_sensors(self):
        data = {
            "name": "basement",
            "temperature": 25,
            "humidity": 57,
            "timestamp": "2020-11-17 11:14:03"
        }
        response = self.client.post('/api/v2/sensors', json=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual('basement', response.json['name'])
        self.assertEqual('2020-11-17 11:14:03', response.json['timestamp'])

    def test_get_a_sensor(self):
        data = {
            "name": "outdoor",
            "temperature": 10,
            "humidity": 70,
            "timestamp": "2020-11-20 13:17:03"
        }
        response = self.client.post('/api/v2/sensors', json=data)
        response = self.client.get('/api/v2/sensors/outdoor')
        self.assertEqual(200, response.status_code)
        self.assertEqual('outdoor', response.json['name'])
        self.assertIn('latest', response.json)


if __name__ == '__main__':
    unittest.main()