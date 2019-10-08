import unittest
from app import *


class Test(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_home_page(self):
        """ Test status_code of home page """
        home = self.app.get('/')
        self.assertEqual(home.status_code, 200)


if __name__ == '__main__':
    unittest.main()
