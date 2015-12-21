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

from bs4 import BeautifulSoup
from bs4 import SoupStrainer

__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__baseURL__ = "http://www.addic7ed.com"

def get_params(string_params):
	# Remove first ? from params
	string_params = string_params[1:]
	# Create dictionary with the params
	params = {}
	params = (q.split('=') for q in string_params.split('&'))

	dicti = dict((key, value) for (key, value) in params)
	return dicti

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

def build_show_url(showId, showSeason):
	# show_url = __baseURL__ + "/show/" + showId + "/season/" + showSeason
	show_url = __baseURL__ + "/ajax_loadShow.php?" + "show=" + str(showId) + "&season=" + str(showSeason) + "&langs=" + "|1|"
	return show_url

def subs_array(showURL, showDetails):
	# Get source
	source = urllib2.urlopen(showURL).read()

	# Make the soup
	soup = BeautifulSoup(source, "html.parser")
	# Iterate through rows of first table
	# and generate array with subs details
	subs = []
	for row in soup.find('table').tbody.findAll('tr'):
		if (not row.has_attr("height")) and (row.contents[1].text == str(showDetails['episode'])):
			if not row.contents[6].text == "":
				hi = "true"
			else:
				hi = "false"

			sub = {
				"season": 		row.contents[0].text,
				"episode": 		row.contents[1].text,
				"episodeTitle":	row.contents[2].contents[0].text,
				"showTitle":	showDetails["showtitle"],
				"lang":			row.contents[3].text,
				"version":		row.contents[4].text,
				"hi":			hi,
				"link":			row.find_all('a')[1].get('href'),
			}
			subs.append(sub.copy())
	return subs

def create_list(subs):
	for sub in subs:
		listitem = xbmcgui.ListItem(label = sub["lang"],
									label2	= "[" + str(sub["version"]) + "]" +
										str(sub["showTitle"]) + " - " + str(sub["episodeTitle"]) + " " +
										"S" + str(sub["season"]) + "E" + str(format(int(sub["episode"]), '02d')),
									iconImage = "",
									thumbnailImage = xbmc.convertLanguage(sub['lang'], xbmc.ISO_639_1))
		# listitem.setProperty("hearing_imp", "true")
		# url = "plugin://%s/?action=download&link=%s&ID=%s&filename=%s&format=%s" % (__scriptid__,
  #                                                                         "",
  #                                                                         "",
  #                                                                         "",
  #                                                                         "",
  #                                                                         )
		xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url="plugin://",listitem=listitem,isFolder=False)


params = get_params(sys.argv[2])
for x in params:
	print(x + ':' + params[x])

show_details = get_details_from_player()
show_id = get_show_id(show_details['showtitle'])
showURL = build_show_url(show_id, show_details['season'])
subs = subs_array(showURL, show_details)
create_list(subs)

xbmcplugin.endOfDirectory(int(sys.argv[1]))