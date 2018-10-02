# -*- coding: utf-8 -*-
"""
	domino.handle
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.handle.user import NICK, USER, PING, PRIVMSG, NOTICE, MODE, WHOIS
from domino.handle.chan import  JOIN, PART, WHO, NAMES, TOPIC
from domino.handle.serv import USERS
from domino.handle.oper import OPER, KILL

def _unknown(user):
	pass

__all__ = ['NICK', 'USER', 'PING', 'PRIVMSG', 'NOTICE', 'MODE', 'WHOIS']
__all__ += [ 'PART', 'JOIN', 'NAMES', 'WHO', 'TOPIC']
__all__ += ['USERS']
__all__ += ['OPER']
