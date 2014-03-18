#coding: utf-8
import logging
import ipdb

from django.contrib.auth import hashers
from mongoengine import (
        Document, StringField, BooleanField, ListField, UUIDField
    )


logger = logging.getLogger(__name__)

class User(Document):
    #TODO Why there is a '_cls' field in db?
    username = StringField(required=True)
    password = StringField(required=True)
    is_superuser = BooleanField(default=False)
    device_ids = ListField(UUIDField(binary=True), default=list)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'password']
    meta = {
        'allow_inheritance': True,
        'indexes': ['username', 'device_ids'],
    }

    def get_username(self):
        "Return the identifying username for this User"
        return self.username

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def is_active(self):
        return True

    def set_password(self, raw_password):
        self.password = hashers.make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return hashers.check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = hashers.make_password(None)

    def has_usable_password(self):
        return hashers.is_password_usable(self.password)

    @classmethod
    def create_user(cls, username, password, is_superuser=False):
        user = cls(username=username, is_superuser=is_superuser)
        user.set_password(password)
        user.save()
        return user

    def my_emails(self):
        # import here to avoid circular reference
        from .email import Email
        return Email.objects(user=self.id)

    @classmethod
    def exist(cls, **kwargs):
        return cls.objects(**kwargs).first()
