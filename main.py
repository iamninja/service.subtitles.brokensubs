# -*- coding: utf-8 -*-

from resources.lib import kodilogging
from resources.lib import subtitle

import logging
import xbmcaddon

# Keep this file to a minimum, as Kodi
# doesn't keep a compiled copy of this
ADDON = xbmcaddon.Addon()
kodilogging.config()

subtitle.run()