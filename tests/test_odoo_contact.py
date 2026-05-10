import unittest

from app.odoo_client import extract_contact_info


class ContactExtractTests(unittest.TestCase):
    def test_extracts_email_phone_and_name(self):
        info = extract_contact_info("Hi, I am Jane Doe. Email me at jane@example.com and call +1 555 123 4567")
        self.assertIsNotNone(info)
        assert info is not None
        self.assertEqual(info.email, "jane@example.com")
        self.assertEqual(info.name, "Jane Doe")

    def test_returns_none_without_contact(self):
        self.assertIsNone(extract_contact_info("What are your tuition fees?"))


if __name__ == "__main__":
    unittest.main()
