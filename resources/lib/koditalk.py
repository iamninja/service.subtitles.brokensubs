# -*- coding: utf-8 -*-
"""Docstring"""

import json
import logging
import xbmc

def pretty_json(ugly_json):
    """Docstring"""
    return json.dumps(json.loads(ugly_json), indent=2, sort_keys=True)

def get_details_from_player():
    """Docstring"""
    logging.debug("addictedutils.get_details_from_player() begin")
    # Create request
    request = {
        "jsonrpc": "2.0",
        "method": "Player.GetItem",
        "params": {
            "properties": [
                "showtitle",
                "season",
                "episode",
                "duration",
                "file"],
            "playerid": 1
        },
        "id": "VideoGetItem"
    }
    # Make request
    response = xbmc.executeJSONRPC(json.dumps(request))
    logging.debug("response: " + pretty_json(response))
    parsed_response = json.loads(response)['result']['item']
    logging.debug("parsed_response: " + json.dumps(parsed_response, indent=2, sort_keys=True))
    return parsed_response
