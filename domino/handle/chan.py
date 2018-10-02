# -*- coding: utf-8 -*-
"""
	domino.handle.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""

from domino.data import DominoData
from domino.chan import Chan
from domino.handle.helpers import send_numeric, split_string_512

def JOIN(user, args):
	if len(args) != 1:
		send_numeric(461, [user.nick, 'JOIN'], ':Not enough parameters')

	def _join(user, chan_str):
		chan = Chan.create_or_get_chan(user, chan_str)
		if not chan:
			send_numeric(403, [user.nickname, chan_str], ':No such nick/channel', user)
		else:
			user.join(chan)

	if '#' not in args[0]:
		send_numeric(403, [user.nickname, chan_str], ':No such nick/channel', user)
	else:
		if ',' in args[0]:
			for chan_str in args[0].split(','):
				_join(user, chan_str)
		else:
			_join(user, args[0])


def PART(user, args):
	if len(args) != 1:
		send_numeric(461, [user.nick, 'PART'], ':Not enough parameters')

	def _part(user, chan_str):
		chan = Chan.create_or_get_chan(user, chan_str)
		if not chan:
			send_numeric(403, [user.nickname, chan_str], ':No such nick/channel', user)
		else:
			user.part(chan)
			
	if '#' not in args[0]:
		send_numeric(403, [user.nickname, chan_str], ':No such nick/channel', user)
	else:
		if ',' in args[0]:
			for chan_str in args[0].split(','):
				_part(user, chan_str)
		else:
			_part(user, args[0])


def NAMES(user, args):
	if len(args) != 1:
		send_numeric(461, [user.nick, 'NAMES'], ':Not enough parameters')

	chan = DominoData.chans.get(args[0].lower())
	if not chan:
		send_numeric(401, [user.nickname, chan_str], ':No such nick/channel', user)
	else:
		chan.names()

def WHO(user, args):
	if len(args) != 1:
		send_numeric(461, [user.nick, 'WHO'], ':Not enough parameters')

	if '#' in args[0]:
		chan = DominoData.chans.get(args[0].lower())
		if not chan:
			send_numeric(401, [user.nickname, chan_str], ':No such nick/channel', user)
		else:
			chan.who(user)

def TOPIC(user, args):
	if '#' in args[0] and len(args) == 2:
		chan = DominoData.chans.get(args[0].lower())
		if not chan:
			send_numeric(401, [user.nickname, args[0]], ':No such nick/channel', user)
		else:
			chan.update_topic(user, args[1])
	else:
		send_numeric(461, [user.nick, 'TOPIC'], ':Not enough parameters')

