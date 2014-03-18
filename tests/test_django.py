from unittest import TestCase

from django.http import HttpResponse

class DjangoTestCase(TestCase):
    def test_long_header(self):
        """A django bug, which hasn't been fixed, see #20889'"""
        h = HttpResponse()
        f = '\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91\xe6\x88\x91'.decode('utf-8')
        h['Content-Disposition'] = u'attachment; filename="%s"' % f
