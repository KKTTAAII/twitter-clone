"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.add(self.testuser)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_show_users(self):
        """Can sign up a user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, html)

    def test_show_user_page(self):
        """Does the page show user's details and msg?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg1 = Message(text="Hello World", user_id=self.testuser.id)
            msg2 = Message(text="Evie is the best doggo", user_id=self.testuser.id)
            db.session.add_all([msg2,msg1])
            db.session.commit()
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg1.text, html)
            self.assertIn(msg2.text, html)
            messages = User.query.get(self.testuser.id).messages
            self.assertEqual(len(messages), 2)

    def test_following(self):
        """Does the page show who is the user following?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            test2 = User.signup(username="u2",
                                    email="u2@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.add(test2)
        db.session.commit()
        test2.following.append(self.testuser)
        resp = c.get(f"/users/{self.testuser.id}/following")
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.testuser.username, html)
    
    def test_follower(self):
        """Does the page show who the user's follower is?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}/following")
            followers = User.query.get(self.testuser.id).followers
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(followers), 0)

    def test_add_likes(self):
        """Test if liking msg works"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message(text="Can I pet that dog?", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()
            resp = c.post(f"/users/add_like/{msg.id}", follow_redirects=True)
            likes = User.query.get(self.testuser.id).likes
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser.id)

    def test_show_liked_msg(self):
        """Does user's like page show all the liked msg?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message(text="Can I pet that dog?", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()

            user = User.query.get(self.testuser.id)
            user.likes.append(msg)
            
            resp = c.get(f"/users/{self.testuser.id}/likes")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Can I pet that dog?", html)

    def test_delete_user(self):
        """Test if the user is deleted"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign up", html)