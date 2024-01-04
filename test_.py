import os
from app import app, session, CURR_USER_KEY, add_user_to_g
from unittest import TestCase
from models import connect_db, db, User, Bookshelf

# USE THIS TO CONNECT TO TESTING DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///book_test'
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