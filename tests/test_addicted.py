# -*- coding: utf-8 -*-
"""Docstring"""

import sys, os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from resources.lib.addictedutils import get_show_id

class ITTests(unittest.TestCase):
    """Docstring"""

    def test_get_show_id(self):
        """Docstring"""
        suits_show_id = get_show_id("Suits")
        ds9_show_id = get_show_id("Star Trek: Deep Space Nine")
        flash_show_id = get_show_id("The Flash (2014)")
        monty_show_id = get_show_id("Monty Python's Flying Circus")
        wtf_show_id = get_show_id("Blå ögon")

        self.assertEqual("1667", suits_show_id)
        self.assertEqual("692", ds9_show_id)
        self.assertEqual("4616", flash_show_id)
        self.assertEqual("6024", monty_show_id)
        self.assertEqual("5158", wtf_show_id)
