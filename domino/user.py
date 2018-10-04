# -*- coding: utf-8 -*-
"""
	domino.user
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import time, socket, hashlib
from domino.parser import IRCProtocol
from domino.handle.helpers import send_numeric
from domino.data import DominoData
from domino.mode import UserMode
from domino.markov import construct_sentence

class User(object):
	def __init__(self, server, conn=None, ip=None, data={}, service=False):
		self.server = server
		if conn:
			self._conn 	= conn
			self._alive = True
			self._ip 	= ip

		self.username 	= data.get('nick') or None
		self.realname 	= data.get('realname') or None
		self.service    = service
		self.realhost	= data.get('virthost') or None
		self.maskhost 	= data.get('virthost') or None
		self.virthost   = data.get('virthost') or None

		self.nick		= data.get('nick') or None
		self.ping 		= int(time.time())
		self.created 	= self.ping
		self.idle 		= self.created
		self.welcomed 	= False
		self.away 		= False
		self.data_user  = None

		self.relatives 	= set()
		self.channels  	= set()
		self.modes 	 	= UserMode(self)

		self.relatives.add(self)

		if self.service:
			self.modes.data['B'] = True

		if self.nick:
			DominoData.users[self.nick.lower()] = self

		if data.get('oper'):
			self.modes.data['O'] = True


	def update_hostname(self):
		if not self.service:
			self.send(':%s NOTICE * :*** Looking up your hostname...' % (self.server.name))
			if DominoData.hosts.get(self._ip[0]):
				self.realhost = DominoData.hosts.get(self._ip[0])
			else:
				try:
					self.realhost = socket.gethostbyaddr(self._ip[0])[0]
					DominoData.hosts[self._ip[0]] = self.realhost

				except:
					self.realhost = self._ip[0]

			if DominoData.masked_hosts.get(self._ip[0]):
				self.maskhost = DominoData.masked_hosts.get(self._ip[0])
			else:
				try:
					_host = self.realhost.split('.')
					endhost = '%s.%s' % (_host[len(_host)-2], _host[len(_host)-1])
					start = construct_sentence(self.server.markov_chain, word_count=4, slug=True)

					self.maskhost = '%s.%s' % (start, endhost)
					DominoData.masked_hosts[self._ip[0]] = self.maskhost
				except:
					self.maskhost = hashlib.new(
						'sha512', 
						self.realhost.encode('utf-8')
					).hexdigest()[:len(self.realhost.encode('utf-8'))] + self.server.config['host_mask']



			self.send(':%s NOTICE * :*** Found your hostname...' % (self.server.name))
			self.send('PING :D%s' % int(time.time()))

	def update_idle(self):
		self.idle = int(time.time())
		self.ping = int(time.time())

	def update_ping(self):
		self.ping = int(time.time())
		

	def update_away(self, value):
		if not value:
			self.away = False
			send_numeric(305, [self.nick], ':You are no longer marked as being away', self)
		else:
			self.away = value
			send_numeric(306, [self.nick], ':You have been marked as being away', self)

	def update_nick(self, new_nick):
		if self.nick in DominoData.users:
			del DominoData.users[self.nick]

		if self.is_ready:
			self.send_relatives(':%s NICK :%s' % (self, new_nick))
		else:
			self.send('PING :D%s' % int(time.time()))

		self.nick = new_nick
		DominoData.users[new_nick.lower()] = self

	def join(self, chan):
		if chan not in self.channels:
			self.channels.add(chan)
			chan.join(self)

	def part(self, chan):
		if chan  in self.channels:
			self.channels.discard(chan)
			chan.part(self)

	def kick(self, source, chan, reason):
		if chan in self.channels:
			self.channels.discard(chan)
			chan.kick(source, self, reason)

	def privmsg(self, target, data, cmd):
		if self.away:
			send_numeric(301, [self.nick, target.nick], ':%s' % (target.away), self)

		if '*' in DominoData.callback['on_privmsg']:
			for callback in DominoData.callback['on_privmsg']['*']:
				data = callback(self, data) or data

		if target.nick.lower() in DominoData.callback['on_privmsg']:
			for callback in DominoData.callback['on_privmsg'][target.nick.lower()]:
				data = callback(self, data) or data

		target.send(':%s %s %s :%s' % (self, cmd, target.nick, data))
		
	def send(self, data):
		if not self.service and self.is_alive:
			try:
				print('>>> %s' % (data))
				data += '\n'
				self._conn[1].write(data.encode('utf-8'))
				self._conn[1].flush()
			except:
				self.die('Rage quit...')

	def send_relatives(self, data, me=True):
		_relatives = self.relatives.copy()
		for relative in _relatives:
			if me == True or relative != self:
				relative.send(data)
		del _relatives

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

			print('######### DEATH #########: %s just died.' % (self))

			for channel in self.channels:
				channel.users.discard(self)

			_relatives = self.relatives.copy()
			for relative in _relatives:
				relative.relatives.discard(self)

			del _relatives

			if self.nick and self.nick.lower() in DominoData.users:	
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
	def is_ready(self):
		if self.service:
			return True

		if self.nick == None or self.username == None or self.hostname == None:
			return False
		return True
	
	@property
	def hostname(self):
		if self.virthost:
			return self.virthost.lower()

		if self.modes.has('x'):
			return self.maskhost.lower()
	
		return self.realhost.lower()


	def __str__(self):
		if self.is_ready:
			return '%s!%s@%s' % (self.nick, self.username, self.hostname)
		else:
			return 'Anonymous!Anonymous@%s' % (self._ip[0])

	def userhost(self):
		if self.is_ready:
			return '%s@%s' % (self.username, self.hostname)

		return ''