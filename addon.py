import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid

def get_params(string_params):
	# Remove first ? from params
	string_params = string_params[1:]
	# Create dictionary with the params
	params = {}
	params = (q.split('=') for q in string_params.split('&'))

	dicti = dict((key, value) for (key, value) in params)
	return dicti

params = get_params(sys.argv[2])
for x in params:
	print(x + ':' + params[x])