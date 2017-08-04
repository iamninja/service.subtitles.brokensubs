# -*- coding: utf-8 -*-
"""Docstring"""

import logging
import requests

from bs4 import BeautifulSoup

BASE_URL = "http://www.addic7ed.com"

def get_language_code(language):
    """Docstring"""
    switcher = {
        "English":    "1",
        "Spanish":    "4",
        "Italian":    "7",
        "French":     "8",
        "Portoguese": "9",
        "Turkish":    "16",
        "Dutch":      "17",
        "Russian":    "19",
        "Romanian":   "26",
        "Greek":      "27",
        "Bulgarian":  "35",
        "Arabic":     "38"
    }
    return switcher.get(language, '')

def build_language_code_string(languages):
    """Docstring"""
    code_string = "|"
    for language in languages:
        code = get_language_code(language)
        if code != "":
            code_string += code + "|"

    if code_string == "|":
        code_string = "|1|"

    return code_string

def build_show_url(show_id, show_season, language_code_string):
    """Docstring"""
    logging.debug("addictedutils.build_show_url() begin")
    show_url = BASE_URL + "/ajax_loadShow.php?"
    show_url += "show=" + str(show_id)
    show_url += "&season=" + str(show_season)
    show_url += "&langs=" + str(language_code_string)
    logging.debug("show_url: " + show_url)
    return show_url

def get_show_id(show_name):
    """Docstring"""
    logging.debug("addictedutils.get_show_id() begin")
    # Get source of addic7ed home page
    source = requests.get(BASE_URL).content.decode('utf-8')

    # Trim source to avoid bad parsing
    string_start = "<span id=\"qssShow\">"
    string_end = "<span id=\"qsSeason\">"
    tag_index_start = source.find(string_start)
    tag_index_end = source.find(string_end)
    source = source[tag_index_start:tag_index_end]

    # Make the soup
    soup = BeautifulSoup(source, "html.parser")
    show_tag = soup.find('option', text=show_name)

    logging.debug("show id: " + show_tag['value'])
    return show_tag['value']
