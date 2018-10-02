# -*- coding: utf-8 -*-
"""
	domino.handle.oper
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512
from domino.mode import UserMode, ChanMode

def KILL(user, args):
	print('KILL', len(args))

	if not user.is_oper:
		send_numeric(481, [user.nick], ':Permission Denied - You\'re not an IRC operator', user)
		return

	if len(args) not in [1,2]:
		return

	target = DominoData.users.get(args[0].lower())

	if not target:
		send_numeric(401, [user.nick, args[0]], ':No such nick/channel', user)
		return

	reason = '...'
	if len(args) == 2:
		reason = args[1]

	target.kill(user, '☠ /killed by %s (%s) ☠' % (user.nick, reason))

def OPER(user, args):
	if user.server.config.get('opers'):
		if user.server.config['opers'].get(args[0]):
			if len(args) == 2:
				if check_password_hash(user.server.config['opers'].get(args[0]), args[1]):
					user.modes.data['O'] = True
					user.modes.data['W'] = True
					user.modes.send()

					send_numeric(381, [user.nick], ':❤ You are now an IRC Operator ❤', user)
					send_numeric(381, [user.nick], ':With great power comes great responsibility...', user)

					return

	send_numeric(464, [user.nick], ':Nice try! ❤', user)
