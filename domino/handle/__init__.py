# -*- coding: utf-8 -*-
"""
	domino.handle
	~~~~~~~~~~~~~~~~
	:license: BSD, see LICENSE for more details.
"""
from domino.handle.user import NICK, USER, PING, JOIN, PART, WHO, NAMES, PRIVMSG, NOTICE

def _unknown(user):
	pass

__all__ = ['NICK', 'USER', 'PING', 'PRIVMSG', 'NOTICE']
__all__ += [ 'PART', 'JOIN', 'NAMES', 'WHO']
