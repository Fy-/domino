# -*- coding: utf-8 -*-
"""
	domino.channel
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time

from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512
from domino.mode import ChanMode

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
		self.modes 		= ChanMode(self)

		DominoData.chans[self.id] = self
		if creator and not self.modes.has('r'):
			self.modes.data['q'].add(creator)
			self.modes.data['a'].add(creator)
			self.modes.data['o'].add(creator)
			self.modes.data['h'].add(creator)
			self.modes.data['v'].add(creator)

	def update_topic(self, user, topic):
		if self.modes.has('t') == False or self.modes.can(user, 'o'):
			self.topic = topic
			self.send(':%s TOPIC %s :%s' % (user, self.name, self.topic))
	
	def join(self, user):
		user.relatives |= self.users
		self.users.add(user)

		for my_user in self.users:
			my_user.relatives.add(user)

		self.send(':%s JOIN %s' % (user, self.name))

		send_numeric(329, [user.nick, self, self.created], '', user)
		if self.topic:
			send_numeric(332, [user.nick, self], ':%s' % (self.topic), user)
		else:
			send_numeric(331, [user.nick, self], ':No topic is set', user)

		self.modes.send(user)
		self.names(user)
		
		if len(self.users) == 1:
			if self.id in DominoData.callback['on_create_chan']:
				for callback in DominoData.callback['on_create_chan'][self.id]:
					callback(user, self)

		if self.id in DominoData.callback['on_join_chan']:
			for callback in DominoData.callback['on_join_chan'][self.id]:
				callback(user, self)



	def privmsg(self, user, data, cmd):
		if self.can_talk(user):

			if self.id in DominoData.callback['on_privmsg_chan']:
				for callback in DominoData.callback['on_privmsg_chan'][self.id]:
					data = callback(user, self, data)

			if '*' in DominoData.callback['on_privmsg_chan']:
				for callback in DominoData.callback['on_privmsg_chan']['*']:
					data = callback(user, self, data)

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
				[
					user.nick, self.name, my_user.hostname, 
					my_user.server.name, my_user.nick, 
					'H%s' % (self.modes.get_prefix(my_user)) if not user.away else 'G%s'  % (self.modes.get_prefix(my_user))
				], 
				':0 %s' % (my_user.realname),
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
	def count(self):
		return len(self.users)
	
	@property
	def user_list(self):
		user_list = ''

		_users = self.users.copy()
		for my_user in _users:
			user_list += ' ' + self.modes.get_prefix(my_user) + my_user.nick 
		del _users

		return user_list.strip(' ')

	def __str__(self):
		return self.name