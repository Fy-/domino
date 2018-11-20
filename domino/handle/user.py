# -*- coding: utf-8 -*-
"""
	domino.handle.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time

from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512
from domino.mode import UserMode, ChanMode
from domino.chan import Chan

def PING(user, args):
	user.update_ping()
	if len(args) == 1:
		user.send(':%s PONG %s :%s' % (user.server.name, user.server.name, args[0]))
	else:
		user.send(':%s PONG %s :%s' % (user.server.name, user.server.name, ''))

def PONG(user, args):
	user.update_ping()
	if len(args) == 1:
		user.send(':%s PING %s :%s' % (user.server.name, user.server.name, args[0]))
	else:
		user.send(':%s PING %s :%s' % (user.server.name, user.server.name, ''))

def QUIT(user, args):
	if len(args) == 1:
		user.quit(args[0])
		return
		
	user.quit('...')
	
def NICK(user, args):
	if len(args) != 1:
		send_numeric(461, [user.nick, 'NICK'], ':Not enough parameters')
		user.send(':%s PING %s :%s' % (user.server.name, user.server.name, ''))
		return

	if DominoData.users.get(args[0].lower()) != None and DominoData.users.get(args[0].lower()) != user:
		send_numeric(433, ['*', args[0]], ':Nickname is already in use.', user)
		user.send(':%s PING %s :%s' % (user.server.name, user.server.name, ''))
		return

	if not DominoData.re_nick.match(args[0]):
		send_numeric(432, ['*', args[0]], ':Erroneous nickname.', user)
		user.send(':%s PING %s :%s' % (user.server.name, user.server.name, ''))
		return

	user.update_nick(args[0])

def NOTICE(user, args):
	PRIVMSG(user, args, 'NOTICE')

def PRIVMSG(user, args, command='PRIVMSG'):
	if len(args) == 1:
		send_numeric(412, [user.nick], ':No text to send', user)
		return
	if len(args) == 0:
		send_numeric(411, [user.nick], ':No recipient given', user)
		return

	if '#'in args[0]:
		chan = DominoData.chans.get(args[0].lower())

		if not chan:
			send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
			return

		chan.privmsg(user, args[1], command)
	else:
		target = DominoData.users.get(args[0].lower())
		if not target:
			send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
			return
		
		user.privmsg(target, args[1], command)


def AWAY(user, args):
	if len(args) == 1:
		user.update_away(args[0])
	elif len(args) == 0:
		user.update_away(False)


def MODE(user, args):
	if len(args) == 0:
		return

	if '#' in args[0]:
		chan = DominoData.chans.get(args[0].lower())
		if not chan:
			send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
			return

		if len(args) == 2:
			chan.modes.send()
		elif len(args) == 3:
			chan.modes.add(user, args)
			
	else:
		user = DominoData.users.get(args[0].lower())
		if not user:
			send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
			return

		if len(args) == 2:
			user.modes.send()
		

def WHOIS(user, args):
	if len(args) not in [1,2]:
		send_numeric(461, [user.nick, 'WHOIS'], ':Not enough parameters', user)
		return

	target = DominoData.users.get(args[0].lower())

	if not target:
		send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
		return

	send_numeric(
		311,
		[user.nick, target.nick, target.username, target.hostname, '*'],
		':%s' % (target.realname),
		user
	)
	send_numeric(379, [user.nick, target.nick], ':is using modes %s' % (target.modes), user)

	if len(user.channels) > 0:
		send_numeric(
			319,
			[user.nick, target.nick],
			':%s' % ' '.join([chan.modes.get_prefix(target) + chan.name for chan in target.channels]),
			user
		)

	if target.away:
		send_numeric(301, [user.nick, target.nick], ':%s' % (target.away), user)

	if target.modes.has('B'):
		send_numeric(335, [user.nick, target.nick], ':is a Bot on %s' % (user.server.name), user)
	if target.is_oper:
		send_numeric(313, [user.nick, target.nick], ':✩✩✩ IRC operator, show some respect! ✩✩✩', user)

	if target.is_registered:
		send_numeric(307, [user.nick, target.nick], ':is identified for this nick', user)
		send_numeric(330, [user.nick, target.nick, target.nick], ':is logged in as', user)

	send_numeric(317, [user.nick, target.nick, (int(time.time()) - target.idle), target.created], ':seconds idle, signon time', user)
	send_numeric(312, [user.nick, target.nick, target.server.name], ':%s' % (user.server.name), user)
	send_numeric(318, [user.nick, target.nick], ':End of /WHOIS list.', user)

def USERHOST(user, args):
	if len(args) == 0:
		return

	user_list = ''
	for user_str in args:
		_user = DominoData.users.get(user_str.lower())
		if _user:
			user_list += ' %s=%s' % (_user.nick, _user.userhost())

	send_numeric(302, [user.nick], ':%s' % (user_list.strip()), user)

def USER(user, args):
	if len(args) != 4:
		user.die("What?")
		return

	if user.is_ready == True:
		send_numeric(462, [user.server.name], ':You may not re-register.', user)
		return

	user.realname = args[3]
	user.username = args[0]

	if user.nick and user.welcomed == False:
		#: Greetings!
		send_numeric(1, [user.nick], ':Welcome to %s %s' % (user.server.name, user.nick), user)
		send_numeric(2, [user.nick], ':Your host is "%s", running version %s' % (user.server.name, user.server.version), user)
		send_numeric(3, [user.nick], ':This server was created on %s' % (user.server.created), user)
		send_numeric(4, [user.nick], '%s %s %s %s' % (user.server.name, user.server.version, UserMode.concat(), ChanMode.concat()), user)
		options_txt = [
			'CMDS=USERIP,STARTTLS,KNOCK,DCCALLOW,MAP UHNAMES NAMESX SAFELIST HCN MAXCHANNELS=30 CHANLIMIT=#:30 MAXLIST=b:60,e:60,I:60 MAXNICKLEN=50 NICKLEN=50 CHANNELLEN=50 TOPICLEN=255 KICKLEN=255',
			'AWAYLEN=255 WALLCHOPS WATCH=128 WATCHOPTS=A SILENCE=15 MODES=12 CHANTYPES=# PREFIX=(ohv)@%+ CHANMODES='+ ChanMode.concat_modes() +' NETWORK=2Kay CHARSET=utf-8',
			'ELIST=MNUCT STATUSMSG=@%+ EXCEPTS INVEX'
		]
		for option_txt in options_txt:
			send_numeric(5, [user.nick], '%s %s :Are supported by this server' % (user.nick, option_txt), user)


		#: Host
		send_numeric(396, [user.nick], '%s :is now your displayed host' % user.hostname, user)

		#: Stats
		send_numeric(251, [user.nick], ':There is %s users on %s' % (len(DominoData.users), user.server.name), user)
		send_numeric(252, [user.nick], ':There is %s channels on %s' % (len(DominoData.chans), user.server.name), user)

		#: MOTD
		send_numeric(252, [user.nick], ':- %s, message of the day -' % (user.server.name), user)
		for l in user.server.motd:
			send_numeric(372, [user.nick], ':- %s' % l.strip('\n'), user)
		send_numeric(376, [user.nick], ':End of /MOTD command', user)


		if len(user.server.config['auto_join']) >= 1:
			for chan_str in user.server.config['auto_join']:
				chan = Chan.create_or_get_chan(user, chan_str)
				user.join(chan)

def ISON(user, args):
	if len(args) == 0:
		return

	user_list = ''
	for user_str in args:
		_user = DominoData.users.get(user_str.lower())
		if _user:
			user_list += ' ' + _user.nick

	send_numeric(303, [user.nick], ':%s' % (user_list.strip()), user)