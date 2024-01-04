import os
import unittest
from app import app, session, CURR_USER_KEY, add_user_to_g
from unittest import TestCase
from models import connect_db, db, User, Bookshelf

# USE THIS TO CONNECT TO TESTING DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///book'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config["TESTING"] = True

db.drop_all()
db.create_all()

client = app.test_client()

class SetUser():
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

form = SetUser(username = "TEST",
               password = "IHeartRob",
               email = "TESTING@testing.com")

class TestUser(TestCase):
    """Tests user login and list"""
    def setUp(self):
        User.query.delete()
        user = User.signup(form.username, form.password,form.email)
        user.password = str(user.password)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """clean up and roll back user login"""
        db.session.rollback()

    def test_redirect(self):
        '''checks logout route, logs you out, and redirects you to /login'''
        resp = client.get("/logout")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "/login")

    def test_homepage(self):
        """checks to see if the logout button is populated on navbar"""
        resp = client.get("/")
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h1>My Google Books API capstone</h1>', html)

    def test_api_book_pull(self):
        """checks to see if a book is pulled by verifying title on book page"""
        resp = client.get('/book/rZz1DwAAQBAJ')
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Love Me Please!', html)


# #Access Control for Unauthenticated Users
# class AccessControlTest(unittest.TestCase):
#     def setUp(self):
#         #the setup method initializes the test client
#         app.testing = True
#         self.app = app.test_client()

#     def test_unauthenticated_access(self):
#         #sends a GET request to the /protected route and asserts that the 
#         #status code is 401 unauthorized
#         response = self.app.get('/protected')
#         self.assertEqual(response.status_code, 401)  




# Backend Tests
# User Authentication Tests
    # Test successful user registration.
    # Test user login with correct credentials.
    # Test login with incorrect credentials.
    # Test access control for unauthenticated users.

# Google Books API Integration Tests
    # Test API call for searching books with valid queries.
    # Test handling of no results from the API.
    # Test API call with invalid or malformed queries.
    # Test error handling for API failures or downtime.

# Favorite List Management Tests
    # Test adding a book to the favorite list.
    # Test removing a book from the favorite list.
    # Test retrieving the favorite list for a user.
    # Test handling of duplicates in the favorite list.

# Frontend Tests

# User Interface Tests
    # Test the login form submission and response handling.
    # Test the registration form submission and response handling.
    # Test redirection or access control for protected routes.

# Search Functionality Tests
    # Test the search input and submission.
    # Test rendering of search results.
    # Test handling of no results found.
    # Test error handling for failed requests.

# Favorite List Interface Tests
    # Test adding books to the favorite list via the UI.
    # Test removing books from the favorite list.
    # Test displaying the favorite list.
    # Test UI feedback for empty favorite lists.