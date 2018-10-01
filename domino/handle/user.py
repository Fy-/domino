# -*- coding: utf-8 -*-
"""
	domino.handle.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.data import DominoData
from domino.chan import Chan
from domino.handle.helpers import send_numeric, split_string_512

def PING(user, args):
	if len(args) == 1:
		user.update_ping(args[0])

def NICK(user, args):
	if len(args) != 1:
		send_numeric(461, [user.nick, 'NICK'], ':Not enough parameters')

	if DominoData.users.get(args[0]) != None and DominoData.users.get(args[0]) != user:
		send_numeric(433, [args[0]], ':Nickname is already in use.', user)
	elif not DominoData.re_nick.match(args[0]):
		send_numeric(433, [args[0]], ':Erroneous nickname.', user)
	else:
		user.update_nick(args[0])

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

def NOTICE(user, args):
	PRIVMSG(user, args, 'NOTICE')

def PRIVMSG(user, args, command='PRIVMSG'):

	if len(args) == 1:
		send_numeric(412, [user.nick], ':No text to send', user)
	elif len(args) == 0:
		send_numeric(411, [user.nick], ':No recipient given', user)
	else:
		if '#'in args[0]:
			chan = DominoData.chans.get(args[0].lower())
			if not chan:
				send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
			else:
				chan.privmsg(user, args[1], command)
				#: on_chan_privmsg
				
		else:
			target = DominoData.users.get(args[0].lower())
			if not target:
				send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
			else:
				user.privmsg(target, args[1], command)


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

def USER(user, args):
	if len(args) != 4:
		#: @TODO: Disconnect client.
		user.die()
		return

	if user.is_ready == True:
		send_numeric(462, [user.server.name], ':You may not re-register.', user)
	else:
		user.realname = args[3]
		user.username = args[0]

		if user.nick and user.welcomed == False:
			#: Greetings!
			send_numeric(1, [user.nick], ':Welcome to %s %s' % (user.server.name, user.nick), user)
			send_numeric(2, [user.nick], ':Your host is "%s", running version %s' % (user.server.name, user.server.version), user)
			send_numeric(3, [user.nick], ':This server was created on %s' % (user.server.created), user)
			send_numeric(4, [user.nick], ':%s %s %s %s' % (user.server.name, user.server.version, 'ADHLNOQSWxrZ', 'AmrnvhoaqbeOlst'), user)
			options_txt = 'CHANTYPES=# CHARSET=utf-8 PREFIX=(qaohv)~&@%+ NICKLEN=50 CHANNELLEN=50 TOPICLEN=390 AWAYLEN=160'
			send_numeric(5, [user.nick], ':%s %s NETWORK=%s :Are supported by this server' % (user.nick, options_txt, user.server.name), user)
			
			#: Stats
			send_numeric(251, [user.nick], ':There is %s users on %s' % (len(DominoData.users), user.server.name), user)
			send_numeric(252, [user.nick], ':There is %s channels on %s' % (len(DominoData.chans), user.server.name), user)

			#: MOTD
			send_numeric(252, [user.nick], ':- %s, message of the day -' % (user.server.name), user)
			for l in user.server.motd:
				send_numeric(372, [user.nick], ':- %s' % (l.strip()), user)
			send_numeric(376, [user.nick], ':End of /MOTD command', user)