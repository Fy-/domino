# -*- coding: utf-8 -*-
"""
	deadpool.nickserv
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import synonym

from deadpool.db import Base, Session
from domino.data import DominoData as domi

class DeadpoolUser(Base):
	__tablename__ = 'user'
	nick = Column(String(50), primary_key=True)
	_password = Column('password', String(120), nullable=False)
	email = Column(String(50))

	def _get_password(self):
		return self._password

	def _set_password(self, password):
		if not password:
			return

		self._password = generate_password_hash(password)

	password = synonym('_password', descriptor=property(_get_password, _set_password))

def nickserv_privmsg(user, args):
	session = Session()
	args = args.split(' ')
	args[0] = args[0].lower()

	nickserv = domi.users.get('nickserv')

	def _ghost(user, args):
		if len(args) != 3:
			nickserv.privmsg(user, 'GHOST	/msg nickserv ghost <nick> <pass>	Kill someone with your nickname.', 'NOTICE')
			return

		_user = session.query(DeadpoolUser).filter(DeadpoolUser.nick == args[1].lower()).first()
		to_kill = domi.users.get(args[1].lower())
		if _user and check_password_hash(_user.password, args[2]) and to_kill and to_kill != user:
			to_kill.kill(user, 'Killed by a bot. FML.')
			user.update_nick(args[1])
			nickserv.privmsg(user, 'Well done. %s has been killed.' % (args[1]), 'NOTICE')
			return

		nickserv.privmsg(user, 'GHOST	Incorrect password (or did you try to kill yourself?).', 'NOTICE')

	def _identify(user, args):
		if len(args) != 2:
			nickserv.privmsg(user, 'IDENTIFY	/msg nickserv identify <pass>	Identify yourself.', 'NOTICE')
			return

		_user = session.query(DeadpoolUser).filter(DeadpoolUser.nick == user.nick.lower()).first()
		if _user and check_password_hash(_user.password, args[1]):
			nickserv.privmsg(user, 'Well done. Hello %s.' % (_user.nick), 'NOTICE')
			user.modes.data['r'] = True
			user.data_user = user
			user.modes.send()
			return

		nickserv.privmsg(user, 'IDENTIFY	Incorrect password. Nice try.', 'NOTICE')

	def _register(user, args):
		if len(args) != 3:
			nickserv.privmsg(user, 'REGISTER	/msg nickserv register <pass> <mail>	Register your current nickname', 'NOTICE')
			return

		exist = session.query(DeadpoolUser).filter(DeadpoolUser.nick == user.nick.lower()).first()
		if exist:
			nickserv.privmsg(user, 'REGISTER	This nickname is already registered.', 'NOTICE')
			return

		_user = DeadpoolUser(nick=user.nick.lower(), password=args[1], email=args[2]) #: @TODO: check email
		session.add(_user)
		nickserv.privmsg(user, 'REGISTER	Well played. You can now use /msg nickserv identify <pass>', 'NOTICE')
		session.commit()

	def _help(user, args):
		nickserv.privmsg(user, 'NickServ allows you to register a nickname.', 'NOTICE')
		nickserv.privmsg(user, '	', 'NOTICE')
		nickserv.privmsg(user, '	GHOST		/msg nickserv ghost <nick> <pass>		Kill someone with your nickname.', 'NOTICE')
		nickserv.privmsg(user, '	IDENTIFY	/msg nickserv identify <pass>			Identify yourself.', 'NOTICE')
		nickserv.privmsg(user, '	REGISTER	/msg nickserv register <pass> <mail>	Register your current nickname', 'NOTICE')
		nickserv.privmsg(user, '	', 'NOTICE')

	if args[0] == 'register':
		_register(user, args)
	elif args[0] == 'identify':
		_identify(user, args)
	elif args[0] == 'ghost':
		_ghost(user, args)
	elif args[0] == 'help':
		_help(user, args)
	else:
		nickserv.privmsg(user, 'Donde esta la biblioteca ?     /msg nickserv help', 'NOTICE')
