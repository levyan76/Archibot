import sys
import types
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Provide a stub for the optional PyMuPDF dependency to allow import
sys.modules.setdefault('fitz', types.ModuleType('fitz'))

import archibot_gpt_deploy.archibot_bot as bot_module


def test_search_keywords_special_chars():
    bot = bot_module.Archibot()
    text = "La norme CAN/CGSB 93.3 s'applique."
    result = bot.search_keywords(text, ["CAN/CGSB 93.3"])
    assert result == ["CAN/CGSB 93.3"]
