# -*- coding: utf-8 -*-
"""
	deadpool.operserv
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from domino.data import DominoData as domi

from deadpool.db import Base, engine, session
from deadpool.chanserv import DeadpoolChan
from deadpool.nickserv import DeadpoolUser

def operserv_privmsg(user, args):
	args = args.split(' ')
	args[0] = args[0].lower()

	operserv = domi.users.get('loki')

	if not user.is_oper:
		operserv.privmsg(user, 'Enough! You are, all of you are beneath me! I am a god, you dull creature, and I will not be bullied ... YOU\'RE NOT A GOD HERE!', 'NOTICE')
		return

	if args[0] == 'init_db':
		Base.metadata.create_all(engine)

		for _user in domi.users.values():
			_user.modes.data['r'] = False
			_user.data_user = None
			_user.modes.send()
			operserv.privmsg(_user, 'Now if you\'ll excuse me, I have to destroy your database.		(db wipe - use /msg nickserv help)', 'NOTICE')
