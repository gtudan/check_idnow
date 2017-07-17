import unittest
import requests_mock
import check_idnow

@requests_mock.Mocker()
class MyTestCase(unittest.TestCase):

    def test_something(self, m):
        m.get('https://gateway.idnow.de/api/v1/me', json={'estimatedWaitingTime': 60, 'numberOfWaitingChatRequests': 1})
        with self.assertRaises(SystemExit) as cm:
            check_idnow.get_waiting_time({'customer_id': 'me', 'hostname': 'gateway.idnow.de', 'warn': 120, 'crit': 600})
        self.assertEqual(cm.exception.code, 0)


if __name__ == '__main__':
    unittest.main()
