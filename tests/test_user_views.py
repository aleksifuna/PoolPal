import unittest
from flask import json
from flask_jwt_extended import create_access_token
from api.v1.app import create_app
from models.user import User
from mongoengine import connect, disconnect

class UserViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Disconnect any existing connections
        disconnect()

        # Create a Flask app instance using the factory
        cls.app = create_app(config_name='test')
        
        # Create a test client
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        # Drop the test database
        disconnect()

    def setUp(self):
        # Clear the database before each test
        User.drop_collection()

    def test_register_user(self):
        response = self.client.post('/api/v1/users', json={
            'first_name': 'John',
            'email': 'john@example.com',
            'phone': '1234567890',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('first_name', data)
        self.assertIn('email', data)
    
    def test_register_user_missing_field(self):
        response = self.client.post('/api/v1/users', json={
            'first_name': 'John',
            'email': 'john@example.com',
            'phone': '1234567890'
            })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Missing password')

    def test_get_user(self):
        response = self.client.post('/api/v1/users', json={
            'first_name': 'John',
            'email': 'john@example.com',
            'phone': '1234567890',
            'password': 'password123'
        })
        user = User.objects(email='john@example.com').first()
        self.assertEqual(response.status_code, 201)
        response = self.client.get(f'/api/v1/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('first_name', data)
        self.assertIn('email', data)

if __name__ == '__main__':
    unittest.main()
