# -*- coding: utf-8 -*-
"""
	domino.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time
from domino.parser import IRCProtocol
from domino.handle.helpers import send_numeric
from domino.data import DominoData
from domino.mode import UserMode

class User(object):
	def __init__(self, server, conn=None, ip=None, data={}):
		self.server = server
		if conn:
			self._conn 	= conn
			self._alive = True
			self._ip 	= ip

		self.username 	= data.get('username') or None
		self.realname 	= data.get('realname') or None

		self.nick		= data.get('nick') or None
		self.ping 		= int(time.time())
		self.created 	= self.ping
		self.idle 		= self.created
		self.welcomed 	= False
		self.away 		= False

		self.relatives 	= set()
		self.channels  	= set()
		self.modes 	 	= UserMode(self)

		self.relatives.add(self)

		self.send(':%s NOTICE * :*** Looking up your hostname...' % (self.server.name))
		self.send(':%s NOTICE * :*** Found your hostname...' % (self.server.name))

		if self.nick:
			DominoData.user[self.nick.lower()] = self

	def update_idle(self):
		self.idle = int(time.time())

	def update_ping(self, arg):
		self.ping = int(time.time())
		self.send('PONG %s :%s' % (self.server.name, arg))

	def update_away(self, value):
		if not value:
			self.away = False
			send_numeric(305, [self.nick], ':You are no longer marked as being away', self)
		else:
			self.away = value
			send_numeric(306, [self.nick], ':You have been marked as being away')

	def update_nick(self, new_nick):
		if self.nick in DominoData.users:
			del DominoData.users[self.nick]

		self.nick = new_nick
		DominoData.users[new_nick.lower()] = self

		if self.is_ready:
			self.send_relatives(':%s NICK :%s' % (self, self.nick))
		else:
			self.send('PING :P%s' % int(time.time()))

	def join(self, chan):
		if chan not in self.channels:
			self.channels.add(chan)
			chan.join(self)

			send_numeric(329, [self.nick, chan, chan.created], '', self)
			if chan.topic:
				send_numeric(332, [self.nick, chan], ':%s' % (chan.topic), self)
			else:
				send_numeric(331, [self.nick, chan], ':No topic is set', self)

			chan.modes.send(self)

			chan.names(self)

	def part(self, chan):
		if chan  in self.channels:
			self.channels.discard(channel)
			chan.part(self)


	def kick(self, source, channel, reason):
		if chan  in self.channels:
			self.channels.discard(channel)
			chan.kick(source, self, reason)

	def privmsg(self, target, data, cmd):
		if self.away:
			send_numeric(301, [self.nick, target.nick], ':%s' % (target.away), self)

		target.send(':%s %s %s :%s' % (self, cmd, target.nick, data))
		
	def send(self, data):
		try:
			if self._alive:
				print ('>>> %s' % (data))
				data += '\r\n'

				self._conn.send(data.encode('utf-8'))
		except (ConnectionResetError):
			self.die('Peer, this bastard.')

	def send_relatives(self, data, me=True):
		_relatives = self.relatives.copy()
		for relative in _relatives:
			if me == True or relative != self:
				relative.send(data)


		del _relatives

	def listen(self):
		while self._alive:
			try:
				data = self._conn.recv(512)
				assert data
				
			except (UnicodeDecodeError, AssertionError, ConnectionResetError):
				self.die('Peer, this bastard.')
				break

			
			IRCProtocol.parse(data, self)
				
		self._conn.close()

	def quit(self, reason=''):
		self.send('%s QUIT :%s' % (self, reason))
		self.die(reason)


	def kill(self, source, reason=''):
		self.send('%s KILL %s :%s' % (self, source.nick, reason))
		self.send('%s QUIT :%s' % (self, reason))
		self.die(reason)

	def die(self, reason=''):
		if self._alive == True:
			self.send_relatives(':%s QUIT :%s' % (self, reason), False)

			self._alive = False

			print('### DEATH: %s just died.' % (self))

			for channel in self.channels:
				channel.users.discard(self)

			_relatives = self.relatives.copy()
			for relative in _relatives:
				relative.relatives.discard(self)

			del _relatives

			
			if self.nick.lower() in DominoData.users:	
				del DominoData.users[self.nick.lower()]

		
	@property
	def is_alive(self):
		return self._alive

	@property
	def is_oper(self):
		return self.modes.has('O')

	@property
	def is_registered(self):
		return self.modes.has('r')

	@property
	def hostname(self):
		return self._ip[0]
	
	@property
	def is_ready(self):
		if self.nick == None or self.username == None or self.hostname == None:
			return False
		return True
	
	
	def __str__(self):
		if self.is_ready:
			return '%s!%s@%s' % (self.nick, self.username, self.hostname)
		else:
			return 'Anonymous!Anonymous@%s' % (self._ip)
