"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="2test@test.com",
            username="2testuser",
            password="2HASHED_PASSWORD"
        )

        db.session.add(u1,u2)
        db.session.commit()

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        User.query.delete()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_repr(self):
        """Does the repr method work as expected?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")

    ##########following tests###########

    def test_follows(self):
        """Does is_following successfully detect when user1 is following user2?"""
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()    

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertEqual(self.u2.is_following(self.u1), False)

    def test_is_followed(self):
        self.u1.following.append(self.u2)
        db.session.commit()    

        self.assertEqual(self.u1.is_followed_by(self.u2), False)
        self.assertEqual(self.u2.is_followed_by(self.u1), True)

    ########user create test############

    def test_create_user(self):
        test = User.signup("testuser3", "test@test.com3", "HASHED_PASSWORD3", None)
        db.session.commit()
        self.assertEqual(test.username, "testuser3")
        self.assertEqual(test.email, "test@test.com3")
        self.assertNotEqual(test.password, "HASHED_PASSWORD")

    def test_create_user_fail(self):
        with self.assertRaises(TypeError) as context:
            User.signup("testuser3", "test@test.com3")

    #########user create authenticate#########

    def test_authenticate_user(self):
        test = User.signup("testuser3", "test@test.com3", "HASHED_PASSWORD3", None)
        db.session.commit()
        test_auth = User.authenticate("testuser3", "HASHED_PASSWORD3")
        self.assertEqual(test_auth.id, test.id)
        self.assertTrue(test_auth)

    def test_authenticate_user_wrong_username(self):
        test = User.signup("testuser3", "test@test.com3", "HASHED_PASSWORD3", None)
        db.session.commit()
        test_auth = User.authenticate("nkfslgb", "HASHED_PASSWORD3")
        self.assertFalse(test_auth)

    def test_authenticate_user_wrong_username(self):
        test = User.signup("testuser3", "test@test.com3", "HASHED_PASSWORD3", None)
        db.session.commit()
        test_auth = User.authenticate("testuser3", "sjgfohnofdhn")
        self.assertFalse(test_auth)
      

   