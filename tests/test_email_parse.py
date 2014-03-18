# coding: utf-8
from unittest import TestCase
from email import message_from_string
from datetime import datetime, timedelta

from gmail import models
from gmail.errors import MessageParseError

class EmailParseTestCase(TestCase):
    def test_decode_rfc2047(self):
        res = models.decode_rfc2047('=?GBK?B?16q8xKO616q8xKO6MTE5z/u3wMjVu+62r82o1qo=?=')
        self.assertIsInstance(res, unicode)
        self.assertEqual(res, u'转寄：转寄：119消防日活动通知')

    def test_decode_rfc2047_with_broken_line(self):
        u = models.decode_rfc2047('=?GB2312?B?ob7Jz7qj1b6hv9PDVmlzdWFsIFN0dWRpbyC/qreiaU9TvLBhbmRyb2lk06bTw6OsxOPSsr/J0tSj\
    oQ==?=')
        self.assertEqual(u, u'【上海站】用Visual Studio 开发iOS及android应用，你也可以！')

    def test_defective_email(self):
        e = message_from_string('Content-Type: multipart/mixed; boundary="ssss"')
        mp = models.MessageParse()
        with self.assertRaises(MessageParseError):
            mp.parse(e)

    def test_pass_invalid_msg_to_parse(self):
        self.assertRaises(TypeError, models.get_email_info, '')

    def test_get_date_info(self):
        msg = message_from_string('Date: Sat, 11 Jan 2014 00:41:13 +0800 (CST)')
        info = models.get_email_info(msg)
        self.assertIn('date', info)
        self.assertEqual(info['date'], datetime(2014, 1, 10, 16, 41, 13))
    
    # def test_default_date_info(self):
    #     msg = message_from_string('SUBject: nothing')
    #     info = models.get_email_info(msg)
    #     self.assertIn('date', info)
    #     self.assertLess(info['date'], datetime.utcnow())
    #     self.assertLess(datetime.utcnow()-info['date'], timedelta(minutes=1))
    
    def test_missing_date(self):
        msg = message_from_string('SUBject: nothing')
        info = models.get_email_info(msg)
        self.assertNotIn('date', info)

        msg = message_from_string('Whatever: Sat, 11 Jan 2014 00:41:13 +08000 (CST)')
        info = models.get_email_info(msg)
        self.assertNotIn('date', info)

    def test_use_date_not_other_matches(self):
        msg = message_from_string('Date: Sat, 11 Jan 2014 00:41:13 +0800 (CST)\nReceived:\
                from m13-147.163.com (Sat, 21 Jan 2014 00:41:15 +0800)')
        info = models.get_email_info(msg)
        self.assertIn('date', info)
        self.assertEqual(info['date'], datetime(2014, 1, 10, 16, 41, 13))

    def test_use_matches_when_date_is_missing(self):
        msg = message_from_string('Received: from m13-147.163.com (Sat, 21 Jan 2014 00:41:15 +0800)')
        info = models.get_email_info(msg)
        self.assertIn('date', info)
        self.assertEqual(info['date'], datetime(2014, 1, 20, 16, 41, 15))

    def test_unstandard_datetime(self):
        msg = message_from_string('Date: 2009-04-02 04:52:08')
        info = models.get_email_info(msg)
        self.assertNotIn('date', info)

    def test_default_content_type(self):
        msg = message_from_string('Date: Sat, 11 Jan 2014 00:41:13 +0800 (CST)')
        info = models.get_email_info(msg)
        self.assertIn('content_type', info)
        self.assertEqual(info['content_type'], 'text/plain')

