# -*- coding: utf-8 -*-
"""
	domino.handle
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.handle.user import NICK, USER, PING, PRIVMSG, NOTICE, MODE, WHOIS, QUIT, ISON, AWAY, USERHOST
from domino.handle.chan import  JOIN, PART, WHO, NAMES, TOPIC
from domino.handle.serv import USERS, LIST
from domino.handle.oper import OPER, KILL

def _unknown(user):
	pass

__all__ = ['NICK', 'USER', 'PING', 'PRIVMSG', 'NOTICE', 'MODE', 'WHOIS', 'QUIT', 'ISON', 'AWAY', 'USERHOST']
__all__ += [ 'PART', 'JOIN', 'NAMES', 'WHO', 'TOPIC']
__all__ += ['USERS', 'LIST']
__all__ += ['OPER', 'KILL']
