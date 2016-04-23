import os
import shutil
import sys
import urllib2
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid
import json

import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

__addon__       = xbmcaddon.Addon()
__scriptid__    = __addon__.getAddonInfo('id')

__profile__     = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
__tempfolder__  = xbmc.translatePath(os.path.join(__profile__, 'temp', '')).decode('utf-8')

__baseURL__     = "http://www.addic7ed.com"

def get_language_code(language):
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
  code_string = "|"
  for language in languages:
    code = get_language_code(language)
    if code != "":
      code_string += code + "|"
  if code_string == "|":
    code_string = "|1|"
  return code_string

def get_params(string_params):
	# Remove first ? from params
	string_params = string_params[1:]
	# Create dictionary with the params
	params = {}
	params = (q.split('=') for q in string_params.split('&'))

	params_in_dictionary = dict((key, value) for (key, value) in params)
	return params_in_dictionary

def get_details_from_player():
	# Create request
	request = {
		"jsonrpc": "2.0",
		"method": "Player.GetItem",
		"params": {
			"properties": ["showtitle", "season", "episode", "duration", "file"],
			"playerid": 1
		},
		"id": "VideoGetItem"
	}
	# Make request
	response = xbmc.executeJSONRPC(json.dumps(request))
	print(response)
	parsed_response = json.loads(response)['result']['item']
	return parsed_response

def get_show_id(showName):
	# Get source
	source = urllib2.urlopen(__baseURL__).read()

	# Trim source to avoid bad parsing
	stringStart = "<span id=\"qssShow\">"
	stringEnd = "<span id=\"qsSeason\">"
	tagIndexStart = source.find(stringStart)
	tagIndexEnd = source.find(stringEnd)
	source = source[tagIndexStart:tagIndexEnd]

	# Make the soup
	soup = BeautifulSoup(source, "html.parser")
	showTag = soup.find('option', text=showName)

	return showTag['value']

def build_show_url(showId, showSeason, language_code_string):
	# show_url = __baseURL__ + "/show/" + showId + "/season/" + showSeason
  show_url = __baseURL__ + "/ajax_loadShow.php?" + "show=" + str(showId) + "&season=" + str(showSeason) + "&langs=" + language_code_string
  # print(show_url)
  return show_url

def subs_array(showURL, showDetails):
  # Get source
  source = urllib2.urlopen(showURL).read()

  # Make the soup
  soup = BeautifulSoup(source, "html.parser")
  # print(soup)
  # Iterate through rows of first table
  # and generate array with subs details
  subs = []
  for row in soup.find('table').tbody.findAll('tr'):
    if (not row.has_attr("height")) and (row.contents[1].text == str(showDetails['episode'])):
      if row.contents[6].text.encode('UTF-8') == u'\u2714':
        hi = 'true'
      else:
        hi = 'false'

      sub = {
      "season": 		    row.contents[0].text,
      "episode": 		    row.contents[1].text,
      "episodeTitle":	    row.contents[2].contents[0].text,
      "showTitle":	    showDetails["showtitle"],
      "lang":			    row.contents[3].text,
      "version":		    row.contents[4].text,
      "hi":			    hi,
      "link":			    row.find_all('a')[1].get('href'),
      }
      # print("HI:" + row.contents[6].text)
      subs.append(sub.copy())
  return subs

def create_list(subs):
    for sub in subs:
        filename = "[" + str(sub["version"].encode('utf8')) + "]" + str(sub["showTitle"].encode('utf8')) + " - " + str(sub["episodeTitle"].encode('utf8')) + " " + "S" + str(sub["season"]) + "E" + str(format(int(sub["episode"]), "02d"))
        listitem = xbmcgui.ListItem(label = sub["lang"],
        							label2	= filename,
        							iconImage = "",
        							thumbnailImage = xbmc.convertLanguage(sub['lang'], xbmc.ISO_639_1))
        listitem.setProperty("hearing_imp", sub["hi"])
        print(filename)
        url = ''
        url = u'plugin://' + __scriptid__ + u'/?action=download&link=' + sub["link"] + u'&filename=' + filename.decode('utf8')
        # url = u'plugin://%s/?action=download&link=%s&filename=%s' % (__scriptid__.encode('utf8'), sub["link"].encode('utf8'), str(filename.encode('utf8')))
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)

def get_sub(link):
    url = __baseURL__ + link
    rheaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2715.0 Safari/537.36',
    'Host': 'www.addic7ed.com',
    'Referer': 'http://www.addic7ed.com'}
    r = requests.get(url, headers = rheaders)
    return r.text

def download(link, filename):
    sub_file = []

    if xbmcvfs.exists(__tempfolder__):
        shutil.rmtree(__tempfolder__)
    xbmcvfs.mkdirs(__tempfolder__)

    file = os.path.join(__tempfolder__, filename.decode('utf8'))
    dfile = get_sub(link)

    file_handler = open(file, "wb")
    file_handler.write(dfile.encode('UTF-8'))
    file_handler.close

    sub_file.append(file)

    return sub_file

params = get_params(sys.argv[2])
for x in params:
	print(x + ':' + params[x].replace("%2c", ","))

if params["action"] == "search":
    languages = params["languages"].replace("%2c", ",").split(",")
    language_code_string = build_language_code_string(languages)
    show_details = get_details_from_player()
    show_id = get_show_id(show_details['showtitle'])
    showURL = build_show_url(show_id, show_details['season'], language_code_string)
    subs = subs_array(showURL, show_details)
    create_list(subs)
elif params["action"] == "download":
    fname = params["filename"].replace(" ", "_") + ".srt"
    subs = download(params["link"], fname)
    for sub in subs:
        listitem = xbmcgui.ListItem(label=sub)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

