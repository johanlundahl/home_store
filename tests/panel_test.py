import unittest
from home_store.models import Panel


class TestPanel(unittest.TestCase):

    def test_not_valid_create(self):
        invalid = {'id': 123, 'name': 'yalla', 'energy': 12}
        self.assertFalse(Panel.valid_create(invalid))
        invalid = {'id': 345, 'name': 'yalla', 'anergy': 12,
                   'alarm_state': True}
        self.assertFalse(Panel.valid_create(invalid))

    def test_valid_create(self):
        valid = {'name': 'yalla', 'id': 1234, 'alarm_state': False,
                 'efficiency': 15, 'energy': 123}
        self.assertTrue(Panel.valid_create(valid))

    def test_create(self):
        valid = {'name': 'yalla', 'energy': 12, 'efficiency': 15,
                 'id': 123456, 'alarm_state': False}
        panel = Panel.create(valid)
        self.assertTrue(isinstance(panel, Panel))
        self.assertEqual('yalla', panel.name)

    def test_panel_to_json(self):
        panel = Panel(12345, 'cliff', 100, False, 95)
        dct = panel.to_json()
        self.assertEqual(dct['panel_id'], 12345)
        self.assertEqual(dct['name'], 'cliff')
        self.assertEqual(dct['energy'], 100)
        self.assertEqual(dct['alarm_state'], False)
        self.assertEqual(dct['efficiency'], 95)
        self.assertTrue('timestamp' in dct)
        self.assertEqual(len(dct), 6)

    def test_panel_to_json_summary(self):
        panel = Panel(12345, 'cliff', 100, False, 95)
        dct = panel.to_json_summary()
        self.assertTrue('id' in dct)
        self.assertTrue('href' in dct)


if __name__ == '__main__':
    unittest.main()
