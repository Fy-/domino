# -*- coding: utf-8 -*-
"""
	domino.parsers
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino import handle

class IRCProtocol(object):
	@staticmethod
	def irc_decode(bytes):
		try:
			text = bytes.decode('utf-8')
		except UnicodeDecodeError:
			try:
				text = bytes.decode('iso-8859-1')
			except UnicodeDecodeError:
				try:
					text = bytes.decode('cp1252')
				except:
					print ('######### ERROR decoding bytes: %s' % (bytes))
					
		return text

	@staticmethod
	def handle_cmd(user, command, args):
		if hasattr(handle, command):
			if user.is_ready or command in ['USER', 'NICK']:
				getattr(handle, command)(user, args)
		else:
			handle._unknown(user)

	@staticmethod
	def parse(line, user):
		if not line or len(line) == 0 or len(line) > 512:
			return

		line = IRCProtocol.irc_decode(line)
		user.update_idle()
		line = line.strip(' \t\n\r')
		print('<<< %s' % (line))
		
		x = line.split(' ', 1)
		command = x[0].upper()

		if len(x) == 1:
			args = []
		else:
			if ':' in x[1]:
				y = x[1].split(':', 1)
				args = y[0].strip(' ').split(' ')
				if len(args) == 1 and len(args[0]) == 0:
					args = []
				args.append(y[1])
			else:
				args = x[1].split(' ')

		IRCProtocol.handle_cmd(user, command, args)
