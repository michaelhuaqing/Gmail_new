from unittest import TestCase

from gmail.HTMLtoText import html2text

class HTMLtoTextTestCase(TestCase):
    def test_strip_tag(self):
        self.assertEqual('what', html2text('<body>what</body>'))

    def test_ignore_script_tag(self):
        self.assertEqual('', html2text('<script>what</script>'))

    def test_ignore_style_tag(self):
        self.assertEqual('', html2text('<style>what</style>'))

    def test_strip_spaces(self):
        self.assertEqual('what', html2text('<body> what </body>'))

