# -*- coding: utf-8 -*-

import urllib2
import requests
import sys
import urlparse
import urllib
import os
import unicodedata
import re
import logging
import codecs
import xbmcgui
import xbmcplugin
import xbmc
import xbmcaddon
import xbmcvfs

import addictedutils

ADDON = xbmcaddon.Addon()
SCRIPT_ID = ADDON.getAddonInfo('id')
PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
TEMP = os.path.join(PROFILE, 'temp', '')
HANDLE = int(sys.argv[1])

# Create the folder where we will store the downloaded subtitles
if not xbmcvfs.exists(TEMP):
    xbmcvfs.mkdirs(TEMP)

def get_params():
    """ Function to retrieve passed parameters, returns a dict.

        Returns:
            The passed parameters as a dictionary.
    """
    if len(sys.argv) > 2:
        return dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))
    return {}

def normalize_string(string):
    """Docstring"""
    return unicodedata.normalize(
        'NFKD', unicode(unicode(string, 'utf-8'))
    ).encode('ascii', 'ignore')

def get_info():
    """ Gather all the information available from the playing item,
        helps to determine what subtitle to list
    """
    item = {}
    item['temp'] = False
    item['rar'] = False
    # Year
    item['year'] = xbmc.getInfoLabel("VideoPlayer.Year")
    # Season
    item['season'] = str(xbmc.getInfoLabel("VideoPlayer.Season"))
    # Episode
    item['episode'] = str(xbmc.getInfoLabel("VideoPlayer.Episode"))
    # Show title
    item['tvshow'] = normalize_string(
        xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))
    # try to get original title
    item['title'] = normalize_string(
        xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))
    # Full path of a playing file
    item['file_original_path'] = urllib.unquote(
        xbmc.Player().getPlayingFile().decode('utf-8'))

    if item['title'] == "":
        # no original title, get just Title
        item['title'] = normalize_string(xbmc.getInfoLabel("VideoPlayer.Title"))
        logging.debug(item['title'])
        logging.debug(item['season'])
        logging.debug(item['episode'])
        # If you didn't get any season, episode or tvshow before try and get it from title.
        regex = re.search(r"\bS(\d.)+E(\d+)\b", item['title'])
        (season, episode) = regex.group(1, 2) if (regex is not None) else ("", "")
        item['season'] = season if item['season'] == '' else item['season']
        item['episode'] = episode if item['episode'] == '' else item['episode']
        if item['tvshow'] == '':
            item['tvshow'] = re.sub(r"\b(S\d.+E\d+)\b", '', item['title']).strip()


    # Check if season is "Special"
    if item['episode'].lower().find("s") > -1:
        item['season'] = "0"
        item['episode'] = item['episode'][-1:]

    # Check if the path is not a local one
    if item['file_original_path'].find("http") > -1:
        item['temp'] = True

    # Check if the path is to a rar file
    elif item['file_original_path'].find("rar://") > -1:
        item['rar'] = True
        item['file_original_path'] = os.path.dirname(
            item['file_original_path'][6:])

    # Check if the path is part of a stack of files
    elif item['file_original_path'].find("stack://") > -1:
        stack_path = item['file_original_path'].split(" , ")
        item['file_original_path'] = stack_path[0][8:]

    # Filename
    item['filename'] = os.path.splitext(
        os.path.basename(item['file_original_path']))[0]
    return item

def get_languages(params, lang_format = 2):
    """
    Get the requested languages the user want to search (3 letter format)

    Args:
        params: The passed parameters dict.
        lang_format: 0 to get full language name
            1 to get two letter code (ISO 639-1)
            2 to get three letter code (ISO 639-2/T or ISO 639-2/B) (default)

    Returns:
        An array with the requested languages, e.g. ['scc','eng']
    """
    langs = []  # ['scc','eng']
    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        if lang_format == 0:
            # Full language name
            langs.append(lang)
        elif lang_format == 1:
            # 2 letter format
            langs.append(xbmc.convertLanguage(lang, xbmc.ISO_639_1))
        else:
            # 3 letter format
            langs.append(xbmc.convertLanguage(lang, xbmc.ISO_639_2))
    return langs

def append_subtitle(subname, lang_name, language, params, sync=False, h_impaired=False):
    """Add the subtitle to the list of subtitles to show"""
    listitem = xbmcgui.ListItem(
        # Languange name to display under the lang logo (for example english)
        label=lang_name,
        # Subtitle name (for example 'Lost 1x01 720p')
        label2=subname,
        # Languange 2 letter name (for example en)
        thumbnailImage=xbmc.convertLanguage(language, xbmc.ISO_639_1))

    # Subtitles synced with the video
    listitem.setProperty("sync", 'true' if sync else 'false')
    # Hearing impaired subs
    listitem.setProperty("hearing_imp", 'true' if h_impaired else 'false')

    # Create the url to the plugin that will handle the subtitle download
    url = "plugin://{url}/?{params}".format(
        url=SCRIPT_ID, params=urllib.urlencode(params))
    # Add the subtitle to the list
    xbmcplugin.addDirectoryItem(
        handle=HANDLE, url=url, listitem=listitem, isFolder=False)

def search(info, languages):
    """Add subtitles to the list using information gathered with get_info and get_languages"""
    logging.debug("---TUCAN---")
    logging.debug(info)
    url = addictedutils.build_show_url(
        addictedutils.get_show_id(info['tvshow']),
        info['season'],
        addictedutils.build_language_code_string(languages))
    logging.debug(url)
    subs = addictedutils.subs_array(url, info)
    #logging.debug(subs)
    for sub in subs:
        sub_name = sub['showTitle'] + " " + sub['season'] + "x" + sub['episode'] + " " + sub['version']
        sub_params = {
            "action": "download-addicted",
            "link": sub['link'],
            "name": sub_name
        }
        append_subtitle(
            sub_name,
            sub['lang'],
            xbmc.convertLanguage(sub['lang'], xbmc.ISO_639_2),
            sub_params,
            sub['sync'],
            sub['himp'])

    #addictedutils.get_details_from_player()

def manual_search(search_str, languages):
    """Add subtitles to the list using user manually inserted string"""
    append_subtitle(
        "Lost 1x01", "English", "eng", {"action": "download", "id": 15}, sync=True)
    append_subtitle("Lost 1x01", "Italian", "ita", {"action": "download", "id": 16})
    append_subtitle("Lost 1x01 720p", "English", "eng", {"action": "download", "id": 17})

def download(params):
    """Download the subtitle chosen by the user"""
    id = params['id']
    # download the file requested
    url = "http://path.to/subtitle/{id}.srt".format(id=id)
    file = os.path.join(TEMP, "{id}.srt".format(id=id))

    response = urllib2.urlopen(url)
    with codecs.open(file, "w", "utf-8") as local_file:
        local_file.write(response.read())

    # give the file to kodi
    xbmcplugin.addDirectoryItem(
        handle=HANDLE, url=file, listitem=xbmcgui.ListItem(label=file), isFolder=False)

def download_addicted(params):
    """Download the subtitle from addic7ed.com"""
    file = os.path.join(TEMP, params['name'] + ".srt")
    dfile = addictedutils.download_subtitle(params['link'])

    with open(file, 'wb',) as local_file:
        local_file.write(dfile.encode('utf-8'))

    # Give the file to kodi
    xbmcplugin.addDirectoryItem(
        handle=HANDLE, url=file, listitem=xbmcgui.ListItem(label=file), isFolder=False)

def run():
    """Docstring"""
    # Gather the request info
    params = get_params()

    if 'action' in params:
        if params['action'] == "search":
            # If the action is 'search' use item information kodi provides to search for subtitles
            search(get_info(), get_languages(params, 0))
        elif params['action'] == "manualsearch":
            # If the action is 'manualsearch' use user manually inserted string to search
            # for subtitles
            manual_search(params['searchstring'], get_languages(params, 0))
        elif params['action'] == "download":
            # If the action is 'download' use the info provided to download the subtitle and give
            # the file path to kodi
            download(params)
        elif params['action'] == "download-addicted":
            # If the action is 'download' use the info provided to download the subtitle and give
            # the file path to kodi
            download_addicted(params)

    xbmcplugin.endOfDirectory(HANDLE)
