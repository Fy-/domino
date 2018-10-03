# -*- coding: utf-8 -*-
"""
	smileys.ext
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import regex as re
from domino.data import DominoData as domi
from smileys.emoji import emoji


    
class ServerSideSmiley(object):
	pattern = re.compile('(:[a-zA-Z0-9\+\-_&.ô’Åéãíç()!#*]+:)')

	def __init__(self):
		print ('[Domino] [ServerSideSmiley] Loading ServerSideSmiley')

	def init(self, server):


		def _replace(user, data):

			def replace_emoji(match):
				m = match.group(1)
				return emoji.get(m, m)

			return ServerSideSmiley.pattern.sub(replace_emoji, data)

		def _replace_chan(user, chan, data):
			return _replace(user, data)

		domi.add_callback('on_privmsg', _replace, key='*')
		domi.add_callback('on_privmsg_chan', _replace_chan, key='*')

		print ('[Domino] [ServerSideSmiley] ❤‿❤ - Loaded')



