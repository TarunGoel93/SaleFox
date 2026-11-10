#!/usr/bin/env python3
"""
Unit verification test for Samsung exact-model isolation & anti-hallucination rules.
"""

from samsung_scraper import SamsungScraper

def test_model_isolation():
    matcher = SamsungScraper.matches_exact_model

    print("Running Model Isolation Rule Checks...")

    # Rule 1: 'Galaxy S24' should match S24, but strictly reject Ultra, Plus, FE
    assert matcher("Galaxy S24", "Samsung Galaxy S24", "Galaxy S24") is True
    assert matcher("Galaxy S24", "Samsung Galaxy S24 Ultra", "Galaxy S24 Ultra") is False
    assert matcher("Galaxy S24", "Samsung Galaxy S24+", "Galaxy S24+") is False
    assert matcher("Galaxy S24", "Samsung Galaxy S24 Plus", "Galaxy S24 Plus") is False
    assert matcher("Galaxy S24", "Samsung Galaxy S24 FE 5G", "Galaxy S24 FE") is False
    print("PASS: Galaxy S24 isolation (rejected Ultra, Plus, FE)")

    # Rule 2: 'Galaxy S24 Ultra' should match only Ultra
    assert matcher("Galaxy S24 Ultra", "Samsung Galaxy S24 Ultra", "Galaxy S24 Ultra") is True
    assert matcher("Galaxy S24 Ultra", "Samsung Galaxy S24", "Galaxy S24") is False
    print("PASS: Galaxy S24 Ultra isolation")

    # Rule 3: 'Galaxy Z Flip 6' should match Flip 6, strictly reject Fold 6
    assert matcher("Galaxy Z Flip 6", "Samsung Galaxy Z Flip 6", "Galaxy Z Flip 6") is True
    assert matcher("Galaxy Z Flip 6", "Samsung Galaxy Z Fold 6", "Galaxy Z Fold 6") is False
    print("PASS: Galaxy Z Flip 6 isolation (rejected Fold 6)")

    # Rule 4: 'Galaxy Z Fold 6' should match Fold 6, strictly reject Flip 6
    assert matcher("Galaxy Z Fold 6", "Samsung Galaxy Z Fold 6", "Galaxy Z Fold 6") is True
    assert matcher("Galaxy Z Fold 6", "Samsung Galaxy Z Flip 6", "Galaxy Z Flip 6") is False
    print("PASS: Galaxy Z Fold 6 isolation (rejected Flip 6)")

    # Rule 5: 'Galaxy A55' should match A55, strictly reject A35
    assert matcher("Galaxy A55", "Samsung Galaxy A55 5G", "Galaxy A55") is True
    assert matcher("Galaxy A55", "Samsung Galaxy A35 5G", "Galaxy A35") is False
    print("PASS: Galaxy A55 isolation (rejected A35)")

    # Rule 6: Accessory filtering
    is_acc = SamsungScraper.is_accessory
    assert is_acc("Samsung Galaxy Watch 7 44mm Bluetooth", "Wearable") is True
    assert is_acc("Samsung Galaxy Buds 3 Pro Silver", "Audio") is True
    assert is_acc("Samsung Galaxy S24 Ultra Silicone Case Gray", "Accessory") is True
    assert is_acc("Samsung 45W Power Adapter with Cable", "Chargers") is True
    assert is_acc("Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)", "Smartphones") is False
    print("PASS: Accessory and Wearables negative filtering")

    print("\nALL 6/6 MODEL ISOLATION & FILTERING UNIT TESTS PASSED!")

if __name__ == "__main__":
    test_model_isolation()
