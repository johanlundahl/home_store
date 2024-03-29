import unittest
from flask_testing import TestCase
from home_store.app import app, mydb
import json


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
        content_type = {"Content-Type": "application/json"}
        response = self.client.get('/api/v2', headers=content_type)
        self.assertEqual(200, response.status_code)

    def test_status(self):
        content_type = {"Content-Type": "application/json"}
        response = self.client.get('/api/v2/status', headers=content_type)
        resp = json.loads(response.data)
        self.assertEqual(200, response.status_code)
        self.assertIn('size', resp)
        self.assertIn('count', resp)
        self.assertIn('oldest', resp)
        self.assertIn('newest', resp)

    def test_get_sensors(self):
        response = self.client.get('/api/v2/sensors/indoor')
        self.assertEqual(404, response.status_code)
        data = {
            "name": "indoor",
            "temperature": 20,
            "humidity": 50,
            "timestamp": "2020-11-20 11:14:03"
        }
        response = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                    content_type='application/json')
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
        post_resp = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                     content_type='application/json')
        self.assertEqual(post_resp.status_code, 200, 'POST #1 failed')
        self.assertEqual(post_resp.status_code, 200, 'POST #1 failed')
        data = {
            "name": "outdoor",
            "temperature": 5,
            "humidity": 65,
            "timestamp": "2020-11-20 11:14:03"
        }
        post_resp = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                     content_type='application/json')
        self.assertEqual(post_resp.status_code, 200, 'POST #2 failed')
        response = self.client.get('/api/v2/sensors')
        resp = json.loads(response.data)
        result = [x['name'] in ['outdoor', 'indoor'] for x in resp]
        self.assertTrue(all(result))

    def test_add_sensors(self):
        data = {
            "name": "basement",
            "temperature": 25,
            "humidity": 57,
            "timestamp": "2020-11-17 11:14:03"
        }
        response = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(200, response.status_code)
        self.assertEqual('basement', response.json['name'])
        self.assertEqual('2020-11-17 11:14:03', response.json['timestamp'])

    def test_add_sensor_without_all_required_arguments(self):
        data = {
            "name": "basement",
            "humidity": 57,
            "timestamp": "2020-11-17 11:14:03"
        }
        response = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_get_a_sensor(self):
        data = {
            "name": "outdoor",
            "temperature": 10,
            "humidity": 70,
            "timestamp": "2020-11-20 13:17:03"
        }
        response = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/v2/sensors/outdoor')
        self.assertEqual(200, response.status_code)
        self.assertEqual('outdoor', response.json['name'])
        self.assertIn('latest', response.json)

    def test_get_a_sensor_with_wrong_querystring(self):
        response = self.client.get('/api/v2/sensors/garage?size')
        self.assertEqual(400, response.status_code)

    def test_sensor_latest(self):
        data = {
            "name": "garage",
            "temperature": 10,
            "humidity": 70,
            "timestamp": "2020-11-20 13:17:03"
        }
        self.client.post('/api/v2/sensors', data=json.dumps(data),
                         content_type='application/json')
        data = {
            "name": "garage",
            "temperature": 20,
            "humidity": 80,
            "timestamp": "2020-11-21 13:17:03"
        }
        self.client.post('/api/v2/sensors', data=json.dumps(data),
                         content_type='application/json')
        data = {
            "name": "garage",
            "temperature": 20,
            "humidity": 80,
            "timestamp": "2020-11-20 14:20:03"
        }
        self.client.post('/api/v2/sensors', data=json.dumps(data),
                         content_type='application/json')
        response = self.client.get('/api/v2/sensors/garage/latest')
        resp = json.loads(response.data)
        self.assertEqual('2020-11-21 13:17:03', resp['timestamp'])

    def test_sensor_min_max(self):
        data = {
            "name": "bedroom",
            "temperature": 10,
            "humidity": 70,
            "timestamp": "2022-12-13 13:17:03"
        }
        resp = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = {
            "name": "bedroom",
            "temperature": 11,
            "humidity": 50,
            "timestamp": "2022-12-13 11:20:03"
        }
        resp = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = {
            "name": "bedroom",
            "temperature": 9,
            "humidity": 80,
            "timestamp": "2022-12-13 13:19:03"
        }
        resp = self.client.post('/api/v2/sensors', data=json.dumps(data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        url = '/api/v2/sensors/bedroom/min-max?date=2022-12-13'
        response = self.client.get(url)
        resp = json.loads(response.data)
        print('*** MIN-MAX ***', resp)
        self.assertEqual(11.0, resp['max']['temperature'])
        self.assertEqual(9.0, resp['min']['temperature'])

    def test_sensor_latest_with_wrong_querystring(self):
        response = self.client.get('/api/v2/sensors/garage/latest?page_size')
        self.assertEqual(400, response.status_code)

    def test_get_sensor_readings(self):
        data = {
            "name": "garage",
            "temperature": 10,
            "humidity": 70,
            "timestamp": "2020-11-20 13:17:03"
        }
        post_response = self.client.post('/api/v2/sensors',
                                         data=json.dumps(data),
                                         content_type='application/json')
        self.assertEqual(200, post_response.status_code)
        response = self.client.get('/api/v2/sensors/garage/readings')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json))
        data = {
            "name": "garage",
            "temperature": 1,
            "humidity": 7,
            "timestamp": "2020-11-20 14:05:03"
        }
        self.client.post('/api/v2/sensors', data=json.dumps(data),
                         content_type='application/json')
        response = self.client.get('/api/v2/sensors/garage/readings')
        self.assertEqual(2, len(response.json))

    def test_get_panel(self):
        data = {
            "id": 123,
            "name": "abc",
            "energy": 10,
            "alarm_state": True,
            "efficiency": 50
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        response = self.client.get('/api/v2/panels/123')
        self.assertTrue(len(response.json) > 0)

    def test_get_panel_for_non_existing_panel(self):
        response = self.client.get('/api/v2/panels/123123123')
        self.assertEqual(response.status_code, 404)

    def test_add_panel_with_incomplete_parameters(self):
        data = {
            "id": 123,
            "name": "abc",
            "alarm_state": True,
            "efficiency": 50
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_panels(self):
        data = {
            "id": 123,
            "name": "abc",
            "energy": 10,
            "alarm_state": True,
            "efficiency": 50
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        data = {
            "id": 123,
            "name": "abc",
            "energy": 20,
            "alarm_state": True,
            "efficiency": 60
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        data = {
            "id": 124,
            "name": "abc",
            "energy": 30,
            "alarm_state": True,
            "efficiency": 70
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')

        response = self.client.get('/api/v2/panels')
        self.assertEqual(len(response.json), 2)

    def test_add_panel(self):
        data = {
            "id": 2345,
            "name": "abc",
            "energy": 10,
            "alarm_state": True,
            "efficiency": 50
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_panel_latest(self):
        data = {
            "id": 25,
            "name": "abc",
            "energy": 10,
            "alarm_state": True,
            "efficiency": 50
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        data = {
            "id": 25,
            "name": "abc",
            "energy": 20,
            "alarm_state": True,
            "efficiency": 60
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')
        data = {
            "id": 25,
            "name": "abc",
            "energy": 30,
            "alarm_state": True,
            "efficiency": 70
        }
        response = self.client.post('/api/v2/panels', data=json.dumps(data),
                                    content_type='application/json')

        response = self.client.get('/api/v2/panels/25/latest')
        self.assertEqual(response.json['energy'], 30)

    def test_get_panel_latest_for_non_existing_panel(self):
        response = self.client.get('/api/v2/panels/123123123/latest')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
