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
    logging.debug("addictedutils.build_show_url() BEGIN")
    show_url = BASE_URL + "/ajax_loadShow.php?"
    show_url += "show=" + str(show_id)
    show_url += "&season=" + str(show_season)
    show_url += "&langs=" + str(language_code_string)
    logging.debug("show_url: " + show_url)
    return show_url

def get_show_id(show_name):
    """Docstring"""
    logging.debug("addictedutils.get_show_id() BEGIN")
    # Get source of addic7ed home page
    source = requests.get(BASE_URL).content.decode('utf-8')
    # logging.debug(source)
    # Trim source to avoid bad parsing
    string_start = "<span id=\"qssShow\">"
    string_end = "<span id=\"qsSeason\">"
    tag_index_start = source.find(string_start)
    tag_index_end = source.find(string_end)
    source = source[tag_index_start:tag_index_end]
    # logging.debug(source)
    # Make the soup
    soup = BeautifulSoup(source, "html.parser")
    show_tag = soup.find('option', text=show_name)
    logging.debug(show_tag)
    logging.debug("show id: " + show_tag['value'])
    return show_tag['value']

def subs_array(show_url, show_details):
    """Docstring"""
    logging.debug("addictedutils.subs_array() BEGIN")
    # Get source
    source = requests.get(show_url).content.decode('utf-8')
    # logging.debug(source)

    # Make the soup
    soup = BeautifulSoup(source, "html.parser")
    # logging.debug("Soup served")

    # Iterate through rows of first table
    # and generate array with subs details
    subs = []
    # logging.debug(show_details['episode'])
    for row in soup.find('table').tbody.findAll('tr'):
        if (not row.has_attr("height")) and (row.contents[1].text == str(int(show_details['episode']))):
            logging.debug("got in")
            if row.contents[7].text.encode('UTF-8') != u'':
                himp = True
            else:
                himp = False
            if row.contents[8].text.encode('UTF-8') != u'':
                sync = True
            else:
                sync = False
            sub = {
                "season": row.contents[0].text,
                "episode": row.contents[1].text,
                "episodeTitle": row.contents[2].contents[0].text,
                "showTitle": show_details['tvshow'],
                "lang":	row.contents[3].text,
                "version": row.contents[4].text,
                "himp": himp,
                "sync": sync,
                "link": row.find_all('a')[1].get('href'),
            }
            subs.append(sub.copy())
    # logging.debug(subs)
    return subs

def download_subtitle(link):
    """Docstring"""
    url = BASE_URL + link
    rheaders = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2715.0 Safari/537.36',
        'Host': 'www.addic7ed.com',
        'Referer': 'http://www.addic7ed.com'}

    response = requests.get(url, headers=rheaders)
    return response.text
