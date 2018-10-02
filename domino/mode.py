# -*- coding: utf-8 -*-
"""
	domino.mode
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.data import DominoData
from domino.handle.helpers import send_numeric, split_string_512

class UserMode(object):
	default_modes = {
		'O' : False, 	#: IRC Operator.
		'Q' : False, 	#: Cannot be kicked from chans,
		'W' : False, 	#: Wallops. Recieve connect, disconnect and traceback notices.
		'x' : True, 	#: Masked hostname. Hides the users hostname or IP address from other users.
		'r' : False,	#: Registered User
	}

	def __init__(self, user):
		self.data = {}
		for mode, value in UserMode.default_modes.items():
			self.data[mode] = value

		self.user = user


	def has(self, mode):
		return self.data.get(mode)

	def send(self):
		self.user.send('MODE %s %s' % (self.user.nick, str(self)))


	@staticmethod
	def concat():
		return ''.join(UserMode.default_modes.keys())


	def __str__(self):
		r = '+'

		for mode, value in self.data.items():
			if value == True:
				r += mode

		return r

class ChanMode(object):

	default_modes = {
		'm' : False, #: Muted
		'r' : False, #: Registered with services
		'n' : True,  #: No messages allowed from users who are not in the channel.
		's' : False, #: Secret
		't' : True,  #: Only operator can set the channel topic.
		'l' : False, #: Limited amount of users

		'q' : set(),
		'a' : set(),
		'o' : set(),
		'v' : set(),
		'h' : set()
	}
	symbols = {
		'q' : '~',
		'a' : '&',
		'o' : '@',
		'h' : '%',
		'v' : '+'
	}


	def __init__(self, chan):
		self.data = {}
		for mode, value in ChanMode.default_modes.items():
			self.data[mode] = value

		self.chan = chan

	def can(self, user, needed):
		if user.modes.has('O'):
			return True

		if needed == 'q' and self.get_prefix(user) == '~':
			return True

		if needed == 'a' and self.get_prefix(user) in ['~', '&']:
			return True

		if needed == 'o' and self.get_prefix(user) in ['~', '&', '@']:
			return True

		if needed == 'h' and self.get_prefix(user) in ['~', '&', '@', '%']:
			return True

		if needed == 'v' and self.get_prefix(user) in ['~', '&', '@', '%', '+']:
			return True	

		return False


	def has(self, mode):
		return self.data.get(mode)

	def send(self, user):
		str_modes = '+'
		args = ''
		for mode, value in self.data.items():
			if value == True:
				str_modes += mode
			elif isinstance(value, str):
				args += str(value)

		send_numeric(324, [user.nick, self.chan.name, str_modes, args], '', user)

	def add(self, user, args):
		modes = list(args[1])
		action = modes[0]
		modes = modes[1:]
		for mode in modes:
			if mode in ['m', 'r', 's', 't']:
				if self.can(user, 'o') and len(args) == 3:
					self.data[mode] = True if action == '+' else False
					self.chan.send(':%s MODE %s%s' % (user, self.chan.name, action, mode))
				else:
					send_numeric(461, [user.nick, self.chan.name], ': You\'re not a channel operator', user)
			elif mode in ['l']:
				if self.can(user, 'o'):
					if len(args) == 4 and action == '+':
						self.data[mode] = int(args[3])
						self.chan.send(':%s MODE %s%s %s' % (user, self.chan.name, action, mode, self.data[mode]))
					elif len(args) == 3 and action == '-':
						self.data[mode] = False
						self.chan.send(':%s MODE %s%s' % (user, self.chan.name, action, mode))
				else:
					send_numeric(461, [user.nick, self.chan.name], ': You\'re not a channel operator', user)
			elif mode in ['q', 'a', 'o', 'v', 'h']:
				if len(args) == 3:
					target = DominoData.users.get(args[2].lower())
					if not target:
						send_numeric(403, [user.nick, self.chan.name], ':No such nick/channel', user)
					else:
						if target.can(user, mode):
							changed = False
							if action == '+':
								if target not in self.data[mode]:
									self.data[mode].add(target)
									changed = True
							else:
								if target in self.data[mode]:
									self.data[mode].discard(target)
									changed = True

							if changed:
								self.chan.send(':%s MODE %s %s%s %s' % (user, self.chan.name, action, mode, target.nick))
				else:
					send_numeric(461, [user.nick, 'MODE'], ':Not enough parameters', user)



	def get_prefix(self, user):
		if user in self.data['q']:
			return ChanMode.symbols['q']
		if user in self.data['a']:
			return ChanMode.symbols['a']
		if user in self.data['o']:
			return ChanMode.symbols['o']
		if user in self.data['h']:
			return ChanMode.symbols['h']
		if user in self.data['v']:
			return ChanMode.symbols['v']
		return ''

	@staticmethod
	def concat_symbols():
		return ''.join(ChanMode.symbols.values())

	@staticmethod
	def concat_modes():
		return ''.join(ChanMode.symbols.keys())

	@staticmethod
	def concat():
		return ''.join(ChanMode.default_modes.keys())

