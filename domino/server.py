# -*- coding: utf-8 -*-
"""
	domino.server
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
import datetime, ssl, socket
from threading import Thread

from domino.user import User

__version__ = '0.10.dev'

class Domino(object):
	def __init__(self, config):
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
			with open(config['motd']) as f:
				self.motd = f.readlines()


	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
		sock.bind((self.host, self.port))
		print ('Starting domino on {0}:{1} ...'.format(self.host, self.port))

		while 1:
			sock.listen(0)
			(conn, ip) = sock.accept()

			user = User(server=self, conn=conn, ip=ip)
			Thread(target = user.listen).start()
