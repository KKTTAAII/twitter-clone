"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
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

        db.session.add(u1)
        db.session.commit()

        self.u1 = u1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        User.query.delete()
        db.session.rollback()
        return res
    
    def test_msg_model(self):
        """Does basic model work?"""

        msg = Message(text="hello world", user_id=self.u1.id)
        db.session.add(msg)
        db.session.commit()
        
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(msg.text, "hello world")
        self.assertEqual(msg.user_id, self.u1.id)

    def test_liked_msg(self):
        """test if liked msg is correct msg"""
        
        u2 = User(
            email="Evie@test.com",
            username="EvieCutie",
            password="PASSWORD"
        )
        msg1 = Message(text="liked hello world", user_id=self.u1.id)
        msg2 = Message(text="I love doggos", user_id=self.u1.id)
        db.session.add_all([msg1, msg2])
        db.session.add(u2)
        db.session.commit()

        u2.likes.append(msg2)
        u2.likes.append(msg1)
        self.assertEqual(len(u2.likes), 2)
        self.assertEqual(u2.likes[0].text, "I love doggos")
        self.assertEqual(u2.likes[1].text, "liked hello world")