import os
import sys
import types
import pytest

# Ensure the module can be imported when tests are run from the repo root
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "archibot_gpt_deploy"))

# Provide a minimal stub for the optional PyMuPDF dependency if it's missing
if 'fitz' not in sys.modules:
    sys.modules['fitz'] = types.ModuleType('fitz')

from archibot_bot import Archibot


def test_split_sections():
    text = (
        "Conditions générales\nDetails CG.\n"
        "Revêtements extérieurs\nDetails RE.\n"
        "Béton\nDetails B."
    )
    bot = Archibot()
    sections = bot.split_sections(text)
    assert sections["Conditions générales"] == "Details CG."
    assert sections["Revêtements extérieurs"] == "Details RE."
    assert sections["Béton"] == "Details B."


def test_search_keywords_with_punctuation_and_case_insensitive():
    text = "The spec uses A{2} and b#1 with extras. aama 508 is referenced."
    keywords = ["A{2}", "B#1", "AAMA 508"]
    bot = Archibot()
    found = bot.search_keywords(text, keywords)
    assert set(found) == {"A{2}", "B#1", "AAMA 508"}

