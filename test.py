from unittest import TestCase, main as unittest_main, mock
from bson.objectid import ObjectId
from app import app


sample_playlist_id = ObjectId('5d55cffc4a3d4031f42827a3')

new_user = {
        '_id': sample_playlist_id,
        'user': 'siko408',
        'password': '1234',
        'status': False,  # decides if user is offline
        'cart': [],
        'personal_item': [],
        'admin_status': False,
    }


class Test(TestCase):

    def setUp(self):
        # creates a test client
        self.client = app.test_client()        # propagate the exceptions to the test client
        app.config['TESTING'] = True

    def test_index(self):

        """Test the playlists homepage."""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')

    #def test_creation(self):
    #    user.return_value = new_user
    #    result = self.client.get('/create_user')

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_page(self, mock_find):
        mock_find.return_value = new_user
        print("result:", mock_find)
        result = self.client.get('/create_user')
        print("Result2:", result.data)
        self.assertEqual(result.status, '200 OK')

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_find(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.post('/userpage', data=new_user)
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_item(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.post('/render/user_items', data=new_user)
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_seller(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.get('/seller/stuff')
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)

    @mock.patch('pymongo.collection.Collection.insert_one')
    def test_seller_item_sell(self, mock_insert):
        """Test submitting a new playlist."""
        result = self.client.post('/create/seller/item', data=new_user)
        # After submitting, should redirect to that playlist's page
        self.assertEqual(result.status, '200 OK')

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_inventory(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.get('/inventory/form')
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)


    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_show(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.get('/show_users')
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)


    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_show_find(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.get('/inventory/show')
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_user_loginpage(self, mock_find):
        print("This is the user:", new_user)
        mock_find.return_value = new_user
        result = self.client.get('/login_page')
        self.assertEqual(result.status, '200 OK')
        print("Result2:", result.data)





if __name__ == '__main__':
    unittest_main()
