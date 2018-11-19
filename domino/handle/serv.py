# -*- coding: utf-8 -*-
"""
	domino.handle.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import operator
from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512

def USERS(user, args):
	send_numeric(265, [user.nick, len(DominoData.users)], ':Current local users %s' % (len(DominoData.users)), user)

def LIST(user, args):
	send_numeric(321, [user.nick], 'Channel :Users  Name', user)
	if len(args) in [1,0]:
		for chan in sorted(DominoData.chans.values(), key=operator.attrgetter('count')):
			send_numeric(322, [user.nick, chan.name, chan.count], ':[%s] %s' % (str(chan.modes).strip(" "), chan.topic), user)

	if len(args) == 2:
		all_args = args.split(',')
		_max = 100000000
		_min = -1

		for _arg in _all_args:
			if _arg[0] == '>':
				_max = _arg.split('>')[0]

			elif _arg[0] == '<':
				_max = _arg.split('<')[0]


		i = 0
		for chan in sorted(DominoData.chans.values(), key=operator.attrgetter('count')):
			if chan.count >= _max and chan.count <= _min:
				send_numeric(322, [user.nick, chan.name, chan.count], ':[%s] %s' % (chan.modes, chan.topic), user)
				i = i +1
				if i == 59:
					break

	send_numeric(323, [user.nick], ':End of /LIST', user)
