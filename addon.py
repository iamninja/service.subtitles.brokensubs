import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid
import json

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

params = get_params(sys.argv[2])
for x in params:
	print(x + ':' + params[x])

show_details = get_details_from_player()