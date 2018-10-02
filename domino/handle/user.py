# -*- coding: utf-8 -*-
"""
	domino.handle.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512
from domino.mode import UserMode, ChanMode
from domino.chan import Chan

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


def AWAY(user, args):
	if len(args) == 1:
		user.update_away(args[0])
	elif len(args) == 0:
		user.update_away(False)


def MODE(user, args):
	if '#' in args[0]:
		chan = DominoData.chans.get(args[0].lower())
		if chan:
			if len(args) == 2:
				chan.modes.send()
			elif len(args) == 3:
				chan.modes.add(user, args)
		else:
			send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
	else:
		user = DominoData.users.get(args[0].lower())
		if user:
			if len(args) == 2:
				user.modes.send()
		else:
			send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)


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
			send_numeric(4, [user.nick], ':%s %s %s %s' % (user.server.name, user.server.version, UserMode.concat(), ChanMode.concat()), user)
			options_txt = 'CHANTYPES=# CHARSET=utf-8 PREFIX=({0}){1} NICKLEN=50 CHANNELLEN=50 TOPICLEN=390 AWAYLEN=160'.format(ChanMode.concat_modes(), ChanMode.concat_symbols())
			send_numeric(5, [user.nick], ':%s %s NETWORK=%s :Are supported by this server' % (user.nick, options_txt, user.server.name), user)
			
			#: Stats
			send_numeric(251, [user.nick], ':There is %s users on %s' % (len(DominoData.users), user.server.name), user)
			send_numeric(252, [user.nick], ':There is %s channels on %s' % (len(DominoData.chans), user.server.name), user)

			#: MOTD
			send_numeric(252, [user.nick], ':- %s, message of the day -' % (user.server.name), user)
			for l in user.server.motd:
				send_numeric(372, [user.nick], ':- %s' % (l.strip()), user)
			send_numeric(376, [user.nick], ':End of /MOTD command', user)


			if len(user.server.config['auto_join']) >= 1:
				for chan_str in user.server.config['auto_join']:
					chan = Chan.create_or_get_chan(user, chan_str)
					user.join(chan)