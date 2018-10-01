# -*- coding: utf-8 -*-
"""
	domino.channel
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time

from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512

class Chan(object):
	@staticmethod
	def create_or_get_chan(user, name):
		if DominoData.chans.get(name.lower()):
			return DominoData.chans.get(name.lower())
		else:
			if DominoData.re_chan.match(name):
				chan = Chan(name, creator=user)
				return chan
			else:
				return False

	def __init__(self, name, creator=None):
		self.name 		= name
		self.id 		= name.lower()
		self.users 		= set()
		self.topic 		= ''
		self.created 	= int(time.time())
		self.creator 	= creator

		DominoData.chans[self.id] = self

	def update_topic(self, user, topic):
		pass
	
	def join(self, user):
		user.relatives |= self.users
		self.users.add(user)

		for my_user in self.users:
			my_user.relatives.add(user)

		self.send(':%s JOIN %s' % (user, self.name))

		if len(self.users) == 1:
			pass
			#: on_create_channel

		#: on_join_channel

	def privmsg(self, user, data, cmd):
		if self.can_talk(user):
			self.send(':%s %s %s :%s' % (user, cmd, self.name, data), me=user)
		else:
			send_numeric(404, [user.nick, self.name], ':Cannot send to channel', user)

	def part(self, user):
		user.relatives ^= self.users
		self.users.discard(user)

		for my_user in self.users:
			my_user.relatives.discard(user)

		self.send(':%s PART %s' % (user, self.name))

		if len(self.users) == 0:
			del DominoData.chans[self.id]
			del self

	def kick(self, source, user, r=''):
		user.relatives ^= self.users
		self.users.discard(user)

		for my_user in self.users:
			my_user.relatives.discard(user)

		self.send(':%s KICK %s %s :%s' % (source, self.name, user.nick, r))

		if len(self.users) == 0:
			del DominoData.chans[self.id]
			del self

	def names(self, user):
		for data in split_string_512(self.user_list):
			send_numeric(353, [], '%s = %s :%s' % (user.nick, self.name, data.strip(' ')), user)
		send_numeric(366, [user.nick, self.name], ':End of /NAMES list.', user)


	def who(self, user):
		for my_user in self.users:
			send_numeric(
				352, 
				[user.nick, self.name, user.hostname, user.server.name, user.nick, 'H' if not user.away else 'G'], 
				':%s' % (user.realname),
				user
			)
		send_numeric(315, [user.nick, self.name], ':End of /WHO list.', user)
		
	def can_talk(self, user):
		return True

	def can_join(self, user):
		return True

	def send(self, data, me=False):
		_users = self.users.copy()
		for my_user in _users:
			if me != my_user:
				my_user.send(data)

		del _users

	@property
	def user_list(self):
		user_list = ''

		_users = self.users.copy()
		for my_user in _users:
			user_list += ' ' +  my_user.nick #: @TODO: add prefix

		del _users

		return user_list

	def __str__(self):
		return self.name