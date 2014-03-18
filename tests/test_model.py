# coding: utf-8
import ipdb
from unittest import TestCase
import os.path

from mongoengine import GridFSProxy
from gmail import models

class DeleteTestCase(TestCase):
    def setUp(self):
        fpath = os.path.join(os.path.dirname(__file__), 'fixtures/pic.eml')
        # Add one
        with open(fpath) as fp:
            self.e = models.Email.from_string(fp.read())
        self.e.save()

    def test_delete_resources(self):
        self.assertRegexpMatches(str(self.e.id), r'^\w{24}$')
        self.assertIsInstance(models.Email.objects(id=self.e.id).first(),
                models.Email)

        resources = []
        resources.extend(self.e.resources or [])
        self.assertNotEqual(resources, [])
        resources.extend(self.e.attachments or [])
        resources.append(self.e.source)
        # All exist
        for resc in resources:
            self.assertIsNotNone(GridFSProxy().get(resc.grid_id))

        self.e.delete()
        # None exsits
        self.assertIsNone(models.Email.objects(id=self.e.id).first())
        for resc in resources:
            self.assertIsNone(GridFSProxy().get(resc.grid_id))

    def tearDown(self):
        self.e.delete()

class EmptyBodyTestCase(TestCase):

    def test_empty_body(self):
        e = models.Email.from_string('To: ph0tinia@163.com')
        try:
            # msg.body will be None, in which case we cannot pass it
            # to HTMLParser, who only accepts string
            e.clean()
        except TypeError as e:
            self.fail('%s, may email.body is None' % e)
