# -*- coding: utf-8 -*-
"""
	smileys.ext
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.data import DominoData as domi

class ServerSideSmiley(object):
	def __init__(self):
		print ('[Domino] [ServerSideSmiley] Loading ServerSideSmiley')

	def init(self, server):
		def _replace(user, data):
			smileys = {
				':('      : '😒',
				':)'      : '😊',
				':D'      : '😃',
				'>.<'     : '😆',
				'^^'      : '😄',
				':|'      : '😐',
				':p'      : '😋',
				'=)'      : '㋡',
				'<3'      : '❤',
				':x'      : '☠',
				'(note)'  : '♫',
				'(mail)'  : '✉',
				'(star)'  : '✩',
				'(valid)' : '✔',
				'(flower)': '❀',
				'(plane)' : '✈',
				'(copy)'  : '©',
				'(tel)'   : '☎',
				'x.x'     : '٩(×̯×)۶',
				'o.o'     : 'Ꙩ_Ꙩ',
				'<3.<3'   : '❤‿❤'
			}

			for smiley in smileys:
				data = data.replace(smiley, smileys[smiley])

			return data

		def _replace_chan(user, chan, data):
			return _replace(user, data)

		domi.add_callback('on_privmsg', _replace, key='*')
		domi.add_callback('on_privmsg_chan', _replace_chan, key='*')

		print ('[Domino] [ServerSideSmiley] ❤‿❤ - Loaded')
