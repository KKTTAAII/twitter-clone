"""Message View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_msg(self):
        """can you delete a message as yourself?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        msg = Message(text="hello", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        resp = c.post(f"/messages/{msg.id}/delete")
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Message.query.get(msg.id), None)

    def test_prohibited_adding_msg(self):
        """When you’re logged out, are you prohibited from adding messages?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_prohibited_deleting_msg(self):
        """When you’re logged out, are you prohibited from deleting messages?"""
        with self.client as c:
            msg = Message(text="hello", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_prohibited_adding_msg_not_user(self):
        """are you prohibiting from adding a message as another user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            with self.assertRaises(Exception) as context:
                resp = c.post("/messages/new", data={"text": "Hello"})
                html = resp.get_data(as_text=True)

                user = User.signup("testuser3", "test@test.com3", "HASHED_PASSWORD3", None)
                new_msg = Message(text="hello", user_id=user.id)
                db.session.add(new_msg)
                db.session.commit()

                msg = Message.query.get(new_msg.id)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Access unauthorized.', html)
                self.assertIsNone(msg)
    
    def test_prohibited_deleting_msg_not_user(self):
        """are you prohibiting from deleting a message as another user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            with self.assertRaises(Exception) as context:
                msg = Message(text="hello", user_id=102)
                db.session.add(msg)
                db.session.commit()

                resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
                html = resp.get_data(as_text=True)
                print(html)
                self.assertEqual(resp.status_code, 200)
                self.assertIn('Access unauthorized.', html)