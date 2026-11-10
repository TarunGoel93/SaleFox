"""
Comprehensive test suite for Croma model matcher.
Tests base vs variant isolation, accessory exclusion, generation isolation, and search queries.
"""

import unittest
from model_matcher import is_strict_match, is_accessory_product


class TestCromaModelMatcher(unittest.TestCase):

    def test_accessory_filtering(self):
        # When searching for phone, accessories must be filtered
        match, reason = is_strict_match("iPhone 15", "Spigen Ultra Hybrid Back Case for Apple iPhone 15")
        self.assertFalse(match)
        self.assertEqual(reason, "accessory_filtered")

        match, reason = is_strict_match("iPhone 15", "Apple 20W Type-C Power Adapter / Wall Charger")
        self.assertFalse(match)
        self.assertEqual(reason, "accessory_filtered")

        match, reason = is_strict_match("iPhone 15", "Tempered Glass Screen Protector for iPhone 15")
        self.assertFalse(match)
        self.assertEqual(reason, "accessory_filtered")

        # But if user explicitly requests case, it matches
        match, reason = is_strict_match("iPhone 15 Case", "Spigen Ultra Hybrid Back Case for Apple iPhone 15")
        self.assertTrue(match)

    def test_base_vs_variant_iphone(self):
        # Base iPhone 15 matches authentic base phones
        match, reason = is_strict_match("iPhone 15", "Apple iPhone 15 (128GB, Black)")
        self.assertTrue(match)

        match, reason = is_strict_match("iPhone 15", "Apple iPhone 15 (256GB, Blue)")
        self.assertTrue(match)

        # Base iPhone 15 MUST NOT match Pro, Pro Max, Plus, or older/newer generations
        match, reason = is_strict_match("iPhone 15", "Apple iPhone 15 Pro (128GB, Natural Titanium)")
        self.assertFalse(match)

        match, reason = is_strict_match("iPhone 15", "Apple iPhone 15 Pro Max (256GB, Blue Titanium)")
        self.assertFalse(match)

        match, reason = is_strict_match("iPhone 15", "Apple iPhone 15 Plus (128GB, Pink)")
        self.assertFalse(match)

        match, reason = is_strict_match("iPhone 15", "Apple iPhone 14 (128GB, Midnight)")
        self.assertFalse(match)

        match, reason = is_strict_match("iPhone 15", "Apple iPhone 16 (128GB, Ultramarine)")
        self.assertFalse(match)

    def test_pro_and_pro_max_iphone(self):
        # iPhone 15 Pro matches Pro, NOT base, NOT Pro Max
        match, reason = is_strict_match("iPhone 15 Pro", "Apple iPhone 15 Pro (128GB, Natural Titanium)")
        self.assertTrue(match)

        match, reason = is_strict_match("iPhone 15 Pro", "Apple iPhone 15 Pro Max (256GB, Natural Titanium)")
        self.assertFalse(match)

        match, reason = is_strict_match("iPhone 15 Pro", "Apple iPhone 15 (128GB, Black)")
        self.assertFalse(match)

        # iPhone 15 Pro Max matches only Pro Max
        match, reason = is_strict_match("iPhone 15 Pro Max", "Apple iPhone 15 Pro Max (256GB, Blue Titanium)")
        self.assertTrue(match)

        match, reason = is_strict_match("iPhone 15 Pro Max", "Apple iPhone 15 Pro (128GB, Blue Titanium)")
        self.assertFalse(match)

    def test_galaxy_isolation(self):
        # Base S24 matches S24, not S24 Ultra or S24+
        match, reason = is_strict_match("Galaxy S24", "Samsung Galaxy S24 5G (8GB RAM, 128GB, Onyx Black)")
        self.assertTrue(match)

        match, reason = is_strict_match("Galaxy S24", "Samsung Galaxy S24 Ultra 5G (12GB RAM, 256GB, Titanium Gray)")
        self.assertFalse(match)

        match, reason = is_strict_match("Galaxy S24", "Samsung Galaxy S24 Plus 5G (12GB RAM, 256GB)")
        self.assertFalse(match)

        # S24 Ultra matches S24 Ultra
        match, reason = is_strict_match("Galaxy S24 Ultra", "Samsung Galaxy S24 Ultra 5G (12GB RAM, 256GB, Titanium Black)")
        self.assertTrue(match)

    def test_macbook_isolation(self):
        match, reason = is_strict_match("MacBook Air", "Apple MacBook Air 13.6-inch M3 Chip (8GB RAM, 256GB SSD, Space Gray)")
        self.assertTrue(match)

        match, reason = is_strict_match("MacBook Air", "Apple MacBook Pro 14-inch M3 Pro (18GB RAM, 512GB SSD)")
        self.assertFalse(match)

    def test_wildcard_all(self):
        match, _ = is_strict_match("All", "Sony Bravia 55 inch OLED 4K TV")
        self.assertTrue(match)

        match, _ = is_strict_match("", "Dyson V12 Cordless Vacuum")
        self.assertTrue(match)


if __name__ == "__main__":
    unittest.main()
