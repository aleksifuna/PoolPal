![POOLPAL](https://github.com/aleksifuna/PoolPal/assets/24822934/533bf3cf-3cc7-4757-89b8-cf723e9f2404)
# PoolPal Web Application API

## Overview

This project is a carpooling web application API that enables users to share rides, find available rides, and manage bookings. The application is built with a Python Flask using MongoPy for database interactions and JWT for authentication

## Features

- User registration and authentication
- User profile management
- Create, search, and manage rides
- Book and cancel ride bookings
- Notifications system
- Rating and feedback for rides

## Tech Stack
![PoolPal](https://github.com/aleksifuna/PoolPal/assets/24822934/12244c8d-51c6-498b-9a75-e3f9af7f4c3c)
### Backend

- Python Flask
- MongoPy/ MongoEngine
- JWT for authentication - flask 

### Third party services

- Google distance matrix api
- Mailjar API 

### DevOps

- AWS EC2 - linux server
- Gunicorn
- Nginx


## Installation
1. Clone the repository:
```bash
git clone https://github.com/aleksifuna/PoolPal.git
cd PoolPal
```
2. Create and activate a virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Install and configure MongoDB
- Follow the instructions for your operating system to install MongoDB from the [official MongoDB documentation](https://www.mongodb.com/docs/manual/installation/).
- Start the MongoDB service:
```bash
sudo service mongod start
```
- (Optional) Use mongo shell or a GUI like MongoDB Compass to create a database for the application.

5. Set up environment variables for Flask and database configutation in a .env file
6. Run the application:
```bash
python -m api.v1.app
```

## API Endpoints
### Here are some key endpoints of the PoolPal API:
- User Registration: POST /api/register
- User Login: POST /api/login
- Create a Ride: POST /api/rides
- Search Rides: GET /api/rides
- Book a Ride: POST /api/rides/{ride_id}/book
- Cancel Booking: DELETE /api/rides/{ride_id}/book
- Get Notifications: GET /api/notifications
- Leave Feedback: POST /api/rides/{ride_id}/feedback
- For a complete list of endpoints and to test them, please visit our [Swagger API Documentation](http://34.230.20.180/docs/)

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request. We welcome all contributions.
