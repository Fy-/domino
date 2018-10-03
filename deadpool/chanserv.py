# -*- coding: utf-8 -*-
"""
	deadpool.operserv
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import synonym
import os, random

from deadpool.db import Base, session
from domino.data import DominoData as domi

deadpool_quotes_file = os.path.join(os.path.dirname(__file__), 'quotes.txt')
deadpool_quotes = []
with open(deadpool_quotes_file) as f:
	deadpool_quotes = f.readlines()

def get_random_deadpool_quote():
	return random.choice(deadpool_quotes)

class DeadpoolChan(Base):
	__tablename__ = 'chan'
	id = Column(String(50), primary_key=True)
	name = Column(String(50))
	bot = Column(String(50), index=True, nullable=True)
	topic = Column(String(250), nullable=True)
	id_owner = Column(String(50), ForeignKey('user.nick'))

def chanserv_on_create(user, channel):
	chan = session.query(DeadpoolChan).filter(DeadpoolChan.id == channel.id).first()
	bot = domi.users.get('deadpool')

	if channel not in bot.channels:
		bot.join(channel)
		channel.modes.add(bot, ['', '+r'])
		channel.modes.add(bot, ['', '+ovhqa', bot.nick])

		channel.privmsg(bot, get_random_deadpool_quote(), 'PRIVMSG')
		if chan.topic:
			channel.update_topic(bot, chan.topic)

		for _user in channel.users:
			if _user.nick != bot.nick:
				channel.modes.add(bot, ['', '-ovhqa', _user.nick])
				channel.names(_user)


def chanserv_privmsg(user, args):
	args = args.split(' ')
	args[0] = args[0].lower()
	chanserv = domi.users.get('chanserv')
	botserv  = domi.users.get('deadpool')

	def _help(user, args):
		chanserv.privmsg(user, 'ChanServ allows you to register a channel.', 'NOTICE')
		chanserv.privmsg(user, '	', 'NOTICE')
		chanserv.privmsg(user, '	REGISTER	/msg chanserv register <channel>	Register a channel.', 'NOTICE')
		chanserv.privmsg(user, '	', 'NOTICE')

	def _register(user, args):
		if len(args) == 2:
			chan = domi.chans.get(args[1].lower())
			if not chan:
				chanserv.privmsg(user, 'REGISTER	/msg chanserv register <channel>	-	Incorrect channel.', 'NOTICE')
				return
			if user not in chan.modes.data['q']:
				chanserv.privmsg(user, 'REGISTER	/msg chanserv register <channel>	-	You\'re not the owner of this channel. But nice try.', 'NOTICE')
				return

			exist = session.query(DeadpoolChan).filter(DeadpoolChan.name == chan.name).first()
			if exist:
				chanserv.privmsg(user, 'REGISTER	/msg chanserv register <channel>	-	This channel is already registered.', 'NOTICE')
				return

			if user.modes.data['r'] == False or user.data_user == None:
				chanserv.privmsg(user, 'REGISTER	/msg chanserv register <channel>	-	You need to be logged with NickServ..', 'NOTICE')
				return

			_chan = DeadpoolChan(id=chan.id, name=chan.name, id_owner=user.data_user.nick, bot=botserv.nick)
			session.add(_chan)
			session.commit()
			chan.modes.add(chanserv, ['', '+r'])
			chanserv.privmsg(user, 'Well done, %s is now yours.' % (chan.name), 'NOTICE')
			chanserv_on_create(user, chan)

			return

		chanserv.privmsg(user, 'REGISTER	/msg chanserv register <channel>	-	Register a channel.', 'NOTICE')


	if args[0] == 'register':
		_register(user, args)
	elif args[0] == 'help':
		_help(user, args)
	else:
		chanserv.privmsg(user, 'Donde esta la biblioteca ?	-	/msg nickserv help', 'NOTICE')


def botserv_privmsg(user, channel, args):
	args = args.split(' ')
	args[0] = args[0].lower()
	chan = session.query(DeadpoolChan).filter(DeadpoolChan.id == channel.id).first()

	if not chan:
		return

	if not chan.bot:
		return

	bot = domi.users.get(chan.bot.lower())

	if not bot:
		return

	if args[0] == '!quote':
		channel.privmsg(bot, get_random_deadpool_quote(), 'PRIVMSG')
		return
	if (user.data_user != None and user.data_user.nick == chan.id_owner) or channel.modes.can(user, 'o'):
		if args[0] == '!topic':
			chan.topic = ' '.join(args[1:])
			session.commit()
			channel.update_topic(bot, chan.topic)
		elif args[0] == '!op':
			if len(args) == 1:
				channel.modes.add(bot, ['', '+o', user.nick])
			else:
				_user = domi.users.get(args[1].lower())
				if _user:
					channel.modes.add(bot, ['', '+o', _user.nick])
		elif args[0] == '!deop':
			if len(args) == 1:
				channel.modes.add(bot, ['', '-o', user.nick])
			else:
				_user = domi.users.get(args[1].lower())
				if _user:
					channel.modes.add(bot, ['', '-o', _user.nick])
		elif args[0] == '!voice':
			if len(args) == 1:
				channel.modes.add(bot, ['', '+v', user.nick])
			else:
				_user = domi.users.get(args[1].lower())
				if _user:
					channel.modes.add(bot, ['', '+v', _user.nick])
		elif args[0] == '!devoice':
			if len(args) == 1:
				channel.modes.add(bot, ['', '-v', user.nick])
			else:
				_user = domi.users.get(args[1].lower())
				if _user:
					channel.modes.add(bot, ['', '-v', _user.nick])
		elif args[0] == '!voiceall':
			if len(args) == 1:
				for _user in channel.users:
					channel.modes.add(bot, ['', '+v', _user.nick])
		elif args[0] == '!kick':
			if len(args) == 2:
				_user = domi.users.get(args[1].lower())
				_user.kick(bot, channel, '')
			if len(args) == 3:
				_user = domi.users.get(args[1].lower())
				_user.kick(bot, channel, args[2])
	
	if (user.data_user != None and user.data_user.nick == chan.id_owner) or channel.modes.can(user, 'q'):
		if args[0] == '!owner':
			if len(args) == 1:
				channel.modes.add(bot, ['', '+ovhqa', user.nick])
			else:
				_user = domi.users.get(args[1].lower())
				if _user:
					channel.modes.add(bot, ['', '+ovhqa', _user.nick])
		elif args[0] == '!strip':
			if len(args) == 1:
				channel.modes.add(bot, ['', '-ovhqa', user.nick])
			else:
				_user = domi.users.get(args[1].lower())
				if _user:
					channel.modes.add(bot, ['', '-ovhqa', _user.nick])
