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
			send_numeric(322, [user.nick, chan.name, chan.count], ':[%s] %s' % (chan.modes, chan.topic), user)

	if len(args) == 2:
		print(args[1])
		if args[1][0] == '>' or args[1][0] == '<':
			if args[1][0] == '>':
				for chan in sorted(DominoData.chans.values(), key=operator.attrgetter('count')):
					if chan.count > number:
						send_numeric(322, [user.nick, chan.name, chan.count], ':[%s] %s' % (chan.modes, chan.topic), user)
			elif args[1][0] == '<':
				for chan in sorted(DominoData.chans.values(), key=operator.attrgetter('count')):
					if chan.count < number:
						send_numeric(322, [user.nick, chan.name, chan.count], ':[%s] %s' % (chan.modes, chan.topic), user)
		elif args[1][0] == '*':
			name = args[1].lower().replace('*', '')				
			for chan in sorted(DominoData.chans.values(), key=operator.attrgetter('count')):
				if name in chan.name.lower():
					send_numeric(322, [user.nick, chan.name, chan.count], ':[%s] %s' % (chan.modes, chan.topic), user)

	send_numeric(323, [user.nick], ':End of /LIST', user)
