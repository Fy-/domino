# -*- coding: utf-8 -*-
"""
	domino.server
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import datetime
from threading import Thread

import gevent
import gevent.server
import gevent.monkey
import gevent.pool
from gevent import Greenlet
gevent.monkey.patch_all()

import time

from domino.user import User
from domino.data import DominoData
from domino.markov import create_chain
from domino.parser import IRCProtocol

__version__ = '0.10.dev'

class Domino(object):
	def __init__(self, config):
		print('[Domino] Welcome to domino-ircd')
		self.get_config(config)

	def get_config(self, config):
		default_config = {
			'secret_key': None,
			'name': None,
			'host': '0.0.0.0',
			'port': 6667,
			'debug': False,
			'ipv6': False,
			'ping_timeout': 240.0
		}
		self.config = config

		self.ipv6 = self.config.get('ipv6') or default_config['ipv6']
		self.host = self.config.get('host') or default_config['host']
		self.port = self.config.get('port') or default_config['port']
		self.name = self.config.get('name') or default_config['name']
		self.debug = self.config.get('debug') or default_config['debug']
		self.ping_timeout = self.config.get('ping_timeout') or default_config['ping_timeout']
		self.version = 'Domino %s' % (__version__)
		self.created = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		if config.get('motd'):
			with open(config['motd'], encoding='utf-8') as f:
				self.motd = f.readlines()

		if config.get('hosts_txt'):
			self.markov_chain = create_chain([config.get('hosts_txt')])

	def init(self):
		for data in DominoData.services:
			User(self, data=data, service=True)

	def update_all(self):
		while 1:
			print('		- update_all - check pings and timeouts...')

			_users = [
				user for user in DominoData.users.values()
				if user.service == False and user.is_ready == True and (time.time() - user.ping) > self.ping_timeout
			]
			for user in _users:
				user.die('Ping timeout: {0}'.format(int(time.time() - user.ping)))

			half_timeout = self.ping_timeout / 2.0

			_users = [
				user for user in DominoData.users.values()
				if user.service == False and user.is_ready == True and (time.time() - user.ping) > half_timeout
			]
			for user in _users:
				user.send('PING :D%s' % int(time.time()))

			gevent.sleep(20)

	def handle(self, sock, addr):
		fileobj = sock.makefile('rbwb')
		user = User(server=self, conn=[sock, fileobj], ip=addr)
		user.update_hostname()
		while user.is_alive:
			line = fileobj.readline()

			if not line:
				print('######### killed no line #########')
				user.die('Peer.')
			else:
				IRCProtocol.parse(line, user)

		user.die('I\'m suppose to be already dead.')
		sock.shutdown(gevent.socket.SHUT_RDWR)
		sock.close()

	def run(self):
		print ('[Domino] Starting domino on {0}:{1} ...'.format(self.host, self.port))

		gevent.Greenlet.spawn(self.update_all)

		self.pool = gevent.pool.Pool(10000)
		self.server = gevent.server.StreamServer((self.host, self.port), self.handle, spawn=self.pool)
		self.server.serve_forever()
