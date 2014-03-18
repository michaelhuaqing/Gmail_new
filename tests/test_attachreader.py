#coding: utf-8
from unittest import TestCase
import os.path

from gmail import attachreader

fn_doc = 'fixtures/ping.doc'
fn_pdf = 'fixtures/ping.pdf'

class AttachReaderTestCase(TestCase):
    longMessage = True

    def test_txt_reader(self):
        res = attachreader.read('我的', 'a.txt')
        self.assertIsInstance(res, unicode)
        self.assertEqual(res, u'我的')

    def test_doc_reader(self):
        res = attachreader.read(self.read_binary(fn_doc), fn_doc)
        self.assertEqual(res, 'ping', 'Cannot read MS-Word, try install antiword.')

    def test_pdf_reader(self):
        res = attachreader.read(self.read_binary(fn_pdf), fn_pdf)
        self.assertEqual(res, 'ping', 'Cannot read pdf, try install xpdf.')

    def read_binary(self, fn):
        with open(os.path.join(os.path.dirname(__file__), fn),
                'rb') as fp:
            return fp.read()
